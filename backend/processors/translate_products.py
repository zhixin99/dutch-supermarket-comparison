from deep_translator import GoogleTranslator
from backend.db.supabase_utils import get_supabase, upsert_rows

translation_cache = {}

def translate_cached(text):
    """
    Translate a Dutch product name to English using GoogleTranslator, with an in-memory cache.

    Returns None if text is None or translation fails.
    """
    if not text:
        return None
    
    if text in translation_cache:
        return translation_cache[text]

    try:
        en = GoogleTranslator(source='nl', target='en').translate(text)
        translation_cache[text] = en
        return en
    except Exception as e:
        print(f"[translate_product_names] Translation failed for: {text} | Reason: {e}")
        return None


def translate_missing_product_names(table: str):
    """
    Translate product_name_du → product_name_en
    only for rows where product_name_en IS NULL
    """
    supabase = get_supabase()

    resp = (
        supabase.table(table)
        .select("sku, product_name_du, product_name_en")
        .is_("product_name_en", None)
        .execute()
    )

    rows = resp.data or []
    if not rows:
        print(f"[translate] {table}: nothing to translate")
        return

    updates = []
    for r in rows:
        en = translate_cached(r["product_name_du"])
        if en:
            updates.append(
                {
                    "sku": r["sku"],
                    "product_name_en": en,
                }
            )

    if updates:
        upsert_rows(table, updates, conflict_col="sku")
        print(f"[translate] {table}: translated {len(updates)} rows")