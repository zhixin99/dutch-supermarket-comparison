from __future__ import annotations

import time

import requests

from backend.db.supabase_utils import get_supabase, upsert_rows
from typing import List, Dict, Any

import time
import requests
from typing import Dict, Any, List, Set

from backend.scrapers.utils import normalize_date
from backend.scrapers.utils import normalize_price

# ---------------------------------------------------------------------------
# Fetch products via API
# ---------------------------------------------------------------------------
BASE_URL = "https://api.ah.nl"

BASE_HEADERS = {
	"User-Agent": "Appie/8.60.1",      
	"X-Application": "AHWEBSHOP",     
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Accept-Language": "nl-NL",       
	"Host": "api.ah.nl"
}

def get_access_token():
	url = "https://api.ah.nl/mobile-auth/v1/auth/token/anonymous"
	payload = {"clientId": "appie"} 
	resp = requests.post(url, headers=BASE_HEADERS, json=payload)
	return resp.json()["access_token"]

def auth_headers(access_token: str) -> Dict[str, str]:
	h = BASE_HEADERS.copy()
	h["Authorization"] = f"Bearer {access_token}"
	return h

def get_root_categories(access_token: str) -> List[Dict[str, Any]]:
	"""
	Top-level categories, e.g. 'Aardappel, groente, fruit', 'Vlees', etc.
	It returns a list of objects: 
		[
			{ "id": 6401, 'slugifiedName': 'groente-aardappelen', "name": "Groente en fruit",  },
			{ "id": 3200, "name": "Frisdrank", ... }
			...
		]

	"""
	url = f"{BASE_URL}/mobile-services/v1/product-shelves/categories"
	resp = requests.get(url, headers=auth_headers(access_token), timeout=10)
	resp.raise_for_status()
	data = resp.json()
	return data

def get_subcategories(access_token: str, category_id: int) -> List[Any]:
	"""
	Direct sub-categories for a given category id.
	It returns an object, with a property of "parent", and another property of "children"
	- parent value is the information of the given category_id
	- children value is a list of objects, and each object contain the information of a product
	{'parent': {'id': 6401, 'slugifiedName': 'groente-aardappelen', 'name': 'Groente, aardappelen', 
	'children': [
		{'id': 5159, 'slugifiedName': 'snoepgroente', 'name': 'Snoepgroente', 'images': [{'height': 800, 'width': 800, 'url': 'https://static.ah.nl/dam/product/AHI_43545239393430323031?revLabel=1&rendition=800x800_JPG_Q90&fileType=binary'}, {...}},
		{'id': 1262, 'slugifiedName': 'groentemixen', 'name': 'Groentemixen', 'images': [{'height':....}
	]
	},

	"""
	url = f"{BASE_URL}/mobile-services/v1/product-shelves/categories/{category_id}/sub-categories"
	resp = requests.get(url, headers=auth_headers(access_token), timeout=10)

	if resp.status_code in (204, 404):
		return []

	resp.raise_for_status()
	data = resp.json()

	return data.get("children", [])

def collect_all_taxonomy_ids(access_token: str) -> Set[int]:
	"""
	BFS Traverse the category tree via /categories and /categories/{id}/sub-categories,
	return a set of all category ids (taxonomyIds).

	"""
	roots = get_root_categories(access_token)

	queue: List[int] = []
	
	for cat in roots:
		cid = cat.get("id")
		if cid is not None:
			queue.append(cid)

	# queue = [6401, 21217, 1618, ...]
	print(f"[AH] root categories: {len(queue)}")

	seen: Set[int] = set()

	while queue:
		cid = queue.pop(0)
		if cid in seen:
			continue
		seen.add(cid)

		try:
			subs = get_subcategories(access_token, cid)
		except Exception as e:
			print(f"[AH] warning: failed to fetch sub-categories for {cid}: {e}")
			continue

		for sub in subs:
			sid = sub.get("id")
			if sid is not None and sid not in seen:
				queue.append(sid)

		time.sleep(0.1)
	
	print(f"[AH] collected taxonomy ids: {len(seen)}")
	return seen

def search_products_by_taxonomy(
	access_token: str,
	taxonomy_id: int,
	page: int = 0,
	size: int = 100,
) -> Dict[str, Any]:
	"""
	Search products within a specific taxonomy (category) id.
	"""
	url = f"{BASE_URL}/mobile-services/product/search/v2"
	params = {
		"sortOn": "RELEVANCE",
		"page": page,
		"size": size,
		"taxonomyId": taxonomy_id,
		"adType": "TAXONOMY",
		"availableOnline": "true",
		"orderable": "any",
	}
	resp = requests.get(url, headers=auth_headers(access_token), params=params, timeout=10)

	if resp.status_code == 400:
		print(f"[AH search taxonomy] 400 for taxonomyId={taxonomy_id}, page={page}")
		return {}

	resp.raise_for_status()
	return resp.json()

def fetch_all_products_via_taxonomies(
	access_token: str,
	page_size: int = 100,
) -> List[Dict[str, Any]]:
	"""
	Enumerate *all* products by walking all taxonomyIds (categories + subcategories).
	It returns a list of objects:
	[
		{'webshopId': 497932, 'hqId': 804096, 'title': 'Jan Pannenkoeken naturel', 'salesUnitSize': '675 g', 'unitPriceDescription': 'prijs per kg €5.47', 'images': [{'width': 800, 'height': 800, 'url': 'https://static.ah.nl/dam/product/AHI_4354523130313539303737?revLabel=1&rendition=800x800_JPG_Q90&fileType=binary'}, {'width': 400, 'height': 400, 'url': 'https://static.ah.nl/dam/product/AHI_4354523130313539303737?revLabel=1&rendition=400x400_JPG_Q85&fileType=binary'}, {'width': 200, 'height': 200, 'url': 'https://static.ah.nl/dam/product/AHI_4354523130313539303737?revLabel=1&rendition=200x200_JPG_Q85&fileType=binary'}, {'width': 48, 'height': 48, 'url': 'https://static.ah.nl/dam/product/AHI_4354523130313539303737?revLabel=1&rendition=48x48_GIF&fileType=binary'}, {'width': 80, 'height': 80, 'url': 'https://static.ah.nl/dam/product/AHI_4354523130313539303737?revLabel=1&rendition=80x80_JPG&fileType=binary'}], 'bonusStartDate': None, 'bonusEndDate': None, 'discountType': None, 'segmentType': None, 'promotionType': None, 'bonusMechanism': None, 'currentPrice': None, 'priceBeforeBonus': 3.69, 'orderAvailabilityStatus': 'IN_ASSORTMENT', 'orderAvailabilityDescription': None, 'mainCategory': 'Maaltijden, salades', 'subCategory': 'Pannenkoeken', 'brand': 'Jan', 'shopType': 'AH', 'bonusPeriodDescription': None, 'availableOnline': True, 'isPreviouslyBought': False, 'descriptionHighlights': '<p>Geen tijd om je uit te sloven? Jan heeft het werk al voor je gedaan! Het lekkerste is als je de pannenkoeken even flipt in de pan. Maar je kunt ze ook prima opwarmen in de oven of in de magnetron.</p><p><ul><li>Gemakkelijk en snel op tafel</li><li>Tien stuks: genoeg voor iedereen</li><li>Het allerlekkerst uit de pan - lekker flippen</li></ul></p>', 'propertyIcons': ['vega'], 'stickers': None, 'nutriscore': 'C', 'nix18': False, 'isStapelBonus': False, 'extraDescriptions': [], 'bonusSegmentId': None, 'bonusSegmentDescription': None, 'isBonus': False, 'hasListPrice': None, ....},
		{...},
	]
	"""
	taxonomy_ids = sorted(collect_all_taxonomy_ids(access_token))

	all_products_by_id: Dict[int, Dict[str, Any]] = {}

	for idx, tid in enumerate(taxonomy_ids, start=1):
		print(f"\n[AH taxonomy] ({idx}/{len(taxonomy_ids)}) taxonomyId={tid}")
		page = 0

		while True:
			data = search_products_by_taxonomy(
				access_token, taxonomy_id=tid, page=page, size=page_size
			)
			if not data:
				break

			page_info = data.get("page") or {}
			total_pages = page_info.get("totalPages", page + 1)

			products = data.get("products") or []
			if not products:
				break

			for p in products:
				wid = p.get("webshopId")
				if wid is not None and wid not in all_products_by_id:
					all_products_by_id[wid] = p

			collected = len(all_products_by_id)
			print(
				f"  [AH taxonomy] tid={tid} page {page+1}/{total_pages}, "
				f"products on this page={len(products)}, unique collected={collected}"
			)

			page += 1
			if page >= total_pages:
				break

			time.sleep(0.03)  

	print(f"\n[AH] total unique products collected via taxonomy: {len(all_products_by_id)}")
	return list(all_products_by_id.values())


def map_product_to_row(p: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Map raw AH product JSON -> one row in DataFrame.
	"""
	wid = p.get("webshopId")
	url = f"https://www.ah.nl/producten/product/wi{wid}" if wid is not None else None

	title_raw = p.get("title") or ""
	brand = p.get("brand") or ""
	# title_raw contains brand name. e.g. "AH Latex handschoenen one size". remove the brand name from the title.
	product_name_du = title_raw.strip()
	if brand:
		b = brand.strip()
		if product_name_du.lower().startswith(b.lower() + " "):
			product_name_du = product_name_du[len(b) + 1:].strip()

	unit_du = p.get("salesUnitSize")

	regular_price = p.get("priceBeforeBonus")
	current_price = p.get("currentPrice", regular_price)

	bonus_start = p.get("bonusStartDate")
	bonus_end = p.get("bonusEndDate")

	image = p.get("image")[0].get("url")

	valid_from = None
	valid_to = None
	if bonus_start:
		valid_from = bonus_start  
	if bonus_end:
		valid_to = bonus_end

	return {
		"sku": wid,
		"url": url,
		"product_name_du": product_name_du,
		"unit_du": unit_du,
		"regular_price": regular_price,
		"current_price": current_price,
		"valid_from": valid_from,
		"valid_to": valid_to,
		"brand": brand,
		"image": image
	}


def fetch_all_ah_products(
	page_size: int = 100,
):
	token = get_access_token()
	products = fetch_all_products_via_taxonomies(
		token,
		page_size=page_size,
	)
	rows = [map_product_to_row(p) for p in products]
	return rows


# ---------------------------------------------------------------------------
# Daily refresh for AH
# ---------------------------------------------------------------------------
def refresh_ah_daily():
	"""
	1. Fetch all existing AH products from Supabase -> old_by_sku
	2. Fetch all fresh AH products via API -> new_by_sku
	3. missing_skus = old_skus - new_skus
		 -> availability = False
	4. joint_skus   = old_skus ∩ new_skus
		 -> if price/promo changed -> update
	5. add_skus     = new_skus - old_skus
		 -> insert new products with full info (url, names, unit, brand, prices, etc.)
	"""
	# -------------------------------------------------------------------
	# 1. Fetch existing from Supabase
	# -------------------------------------------------------------------
	supabase = get_supabase()
	resp = supabase.table("ah").select(
		"sku, url, regular_price, current_price, valid_from, valid_to, availability"
	).eq("availability", True).execute()
	old_rows = resp.data or []
	old_by_sku: Dict[str, Dict[str, Any]] = {
		str(r["sku"]): r for r in old_rows if r.get("sku") is not None
	}
	old_skus = set(old_by_sku.keys())
	print(f"[AH daily] Found {len(old_skus)} existing available AH products in DB.")

	# -------------------------------------------------------------------
	# 2. Fetch fresh AH products via API
	# -------------------------------------------------------------------
	fresh_products = fetch_all_ah_products()
	new_by_sku: Dict[str, Dict[str, Any]] = {
		str(p["sku"]): p for p in fresh_products if p.get("sku") is not None
	}
	new_skus = set(new_by_sku.keys())
	print(f"[AH daily] Fetched {len(new_skus)} fresh AH products from API.")

	# -------------------------------------------------------------------
	# 3. Set comparisons
	# -------------------------------------------------------------------
	missing_skus = old_skus - new_skus
	joint_skus = old_skus & new_skus
	add_skus = new_skus - old_skus

	print(f"[AH daily] missing_skus: {len(missing_skus)}")
	print(f"[AH daily] joint_skus:   {len(joint_skus)}")
	print(f"[AH daily] add_skus:     {len(add_skus)}")

	rows_to_upsert: List[Dict[str, Any]] = []

	# -------------------------------------------------------------------
	# 4.1) missing_skus: mark as unavailable
	# -------------------------------------------------------------------
	for sku in missing_skus:
		rows_to_upsert.append(
			{
				"sku": sku,
				"availability": False,
			}
		)

	# -------------------------------------------------------------------
	# 4.2) joint_skus: compare price / promo, update if changed
	# -------------------------------------------------------------------
	for sku in joint_skus:
		old = old_by_sku[sku]
		new = new_by_sku[sku]

		old_cp = normalize_price(old.get("current_price"))
		old_rp = normalize_price(old.get("regular_price"))
		old_vf = normalize_date(old.get("valid_from"))
		old_vt = normalize_date(old.get("valid_to"))

		new_cp = normalize_price(new.get("current_price"))
		new_rp = normalize_price(new.get("regular_price"))
		new_vf = normalize_date(new.get("valid_from"))
		new_vt = normalize_date(new.get("valid_to"))

		if (
			new_cp == old_cp
			and new_rp == old_rp
			and new_vf == old_vf
			and new_vt == old_vt
			and old.get("availability") is True
		):
			continue

		row = {
			"sku": sku,
			"regular_price": new.get("regular_price"),
			"current_price": new.get("current_price"),
			"valid_from": new.get("valid_from"),
			"valid_to": new.get("valid_to"),
			"availability": True,
		}
		rows_to_upsert.append(row)

	# -------------------------------------------------------------------
	# 4.3) add_skus: insert brand-new products
	# -------------------------------------------------------------------
	for sku in add_skus:
		new = new_by_sku[sku]

		rows_to_upsert.append(
			{
				"sku": sku,
				"url": new.get("url"),
				"product_name_du": new.get("product_name_du"),
				"brand": new.get("brand"),
				"unit_du": new.get("unit_du"),
				"regular_price": new.get("regular_price"),
				"current_price": new.get("current_price"),
				"valid_from": new.get("valid_from"),
				"valid_to": new.get("valid_to"),
				"availability": True,
				"image": new.get("image")
			}
		)

	if not rows_to_upsert:
		print("[AH daily] nothing to upsert.")
		return

	print(f"[AH daily] upserting {len(rows_to_upsert)} rows to Supabase...")

	upsert_rows("ah", rows_to_upsert, conflict_col="sku")
	print("[AH daily] Done.")
