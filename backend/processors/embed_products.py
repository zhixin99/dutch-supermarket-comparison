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
        .select("sku, brand, product_name_du, embedding_du")
        .is_("embedding_du", None)
        .not_.is_("product_name_du", None)
        .execute()
    )

    rows = res.data or []
    if not rows:
        print(f"[embed] {table}: no product to embed")
        return

    texts = []
    skus = []
    updates = []

    for r in rows:
        brand = (r.get("brand") or "").strip()
        name = (r.get("product_name_du") or "").strip()

        text = (brand + " " + name).strip()
       
        if not text:
            continue

        skus.append(str(r["sku"]))
        texts.append(text)

    if not skus:
        print(f"[embed] {table}: all {len(rows)} rows have empty names, done.")
        return 
    
    embs = encode_texts(texts)

    updates = [
        {"sku": sku, "embedding_du": emb}
        for sku, emb in zip(skus, embs)
    ]


    if updates: 
        upsert_rows(table, updates, conflict_col="sku")
        print(f"[embed] {table}: embed {len(updates)} rows")
