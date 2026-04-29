# backend/embed_existing_products.py

from __future__ import annotations

from typing import List

from sentence_transformers import SentenceTransformer

from backend.db.supabase_utils import get_supabase, upsert_rows


print("[EMB] loading model...")
EMBED_MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print("[EMB] model loaded.")


def encode_texts(texts: List[str]) -> List[list[float]]:
    if not texts:
        return []

    embs = EMBED_MODEL.encode(
        texts,
        normalize_embeddings=True,
        batch_size=64,
        show_progress_bar=True,
    )
 
    return [vec.astype("float32").tolist() for vec in embs]
    

def embed_missing_products(table: str):
    """
    Embed product brand and name only for rows where embedding_du is NULL
    """
    supabase = get_supabase()

    res = (
        supabase.table(table)
        .select("sku, brand, product_name_du, product_name_en, embedding_du, embedding_en")
        .or_("embedding_du.is.null,embedding_en.is.null")
        .not_.is_("product_name_du", None)
        .execute()
    )

    rows = res.data or []
    if not rows:
        print(f"[embed] {table}: no product to embed")
        return


    batch_texts = []
    batch_metadata = [] # To keep track of which SKU and which Language each embedding belongs to

    for r in rows:
        sku = str(r["sku"])
        brand = (r.get("brand") or "").strip()
        
        # Check Dutch
        if r.get("embedding_du") is None and r.get("product_name_du"):
            name_du = r.get("product_name_du").strip()
            text_du = f"{brand} {name_du}".strip()
            if text_du:
                batch_texts.append(text_du)
                batch_metadata.append({"sku": sku, "lang": "du"})

        # Check English
        if r.get("embedding_en") is None and r.get("product_name_en"):
            name_en = r.get("product_name_en").strip()
            text_en = f"{brand} {name_en}".strip()
            if text_en:
                batch_texts.append(text_en)
                batch_metadata.append({"sku": sku, "lang": "en"})

    if not batch_texts:
        print(f"[embed] {table}: Found rows with NULLs but no valid text to embed.")
        return 

    print(f"[embed] Processing {len(batch_texts)} new embeddings...")
    embs = encode_texts(batch_texts)

    # Now we reorganize the flat list of embeddings back into a format Supabase understands
    # We use a dictionary keyed by SKU to group updates for the same product
    updates_map = {}

    for i, meta in enumerate(batch_metadata):
        sku = meta["sku"]
        lang = meta["lang"]
        embedding = embs[i]

        if sku not in updates_map:
            updates_map[sku] = {"sku": sku}
        
        # This adds 'embedding_du' or 'embedding_en' to the update object
        updates_map[sku][f"embedding_{lang}"] = embedding

    # Convert map back to list for upsert
    final_updates = list(updates_map.values())

    if final_updates: 
        upsert_rows(table, final_updates, conflict_col="sku")
        print(f"[embed] {table}: Successfully updated {len(final_updates)} products.")
