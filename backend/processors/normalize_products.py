import re
import pandas as pd
from backend.db.supabase_utils import get_supabase, upsert_rows

def normalize_unit(unit_text: str):
    """
    Converts messy Dutch unit into a string with the format of unit_qty unit_type
    - unit_qty is a number
    - unit_type ∈ {"kg", "l", "piece"} 
    - return None if unknown
    """
    if pd.isna(unit_text) or unit_text is None:
        return None

    s = unit_text.strip().lower()

    s = s.replace(",", ".")
    s = s.replace("×", "x")  
    s = s.replace("stuks", "stuk")
    s = s.replace("st.", "stuk")


    # "5-pack" -> "5 pack"
    s = s.replace("-"," ")      

    # "ca. 115 g" -> "115 g"
    s = s.replace("ca. ", "")    

    # "ca 444 g" -> "444 g"
    s = s.replace("ca ", "")        

    # "los per 500 g" -> "500 g"
    s = s.replace("los per ", "")    

    #"0. 75" -> "0.75"
    s = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', s)

    # "2-3 pers | 20 min" -> "1 piece"
    if "|" in s:
        s = s.split("|", 1)[0].strip()
    if re.search(r"\bpers(?:oon|onen)?\b", s):
        return "1 piece"
    
    # "per 500 g" -> "500 g", "per stuk" -> "stuk"
    s = re.sub(r"^\s*per\s+", "", s) 
    # "stuk" -> "1 stuk"
    if not any(i.isdigit() for i in s): 
        s = "1 " + s

    # "1 kg (ca. 5 stuk)" -> 1 kg
    s = s.split("(")[0].strip()      

    # "6 x 250 g" -> "1500 g"
    m = re.match(r"(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", s)
    if m:
        count = float(m.group(1))
        size = float(m.group(2))
        unit_type = m.group(3).split()[0] # eg. "6 x 250 g appel" -> drop "appel"
        unit_qty = size * count
        s = str(unit_qty) + unit_type

    # "4 + 2 stuks" -> "6 stuks"
    m = re.match(r"(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", s)
    if m:
        unit_qty = float(m.group(1)) + float(m.group(2))
        unit_type = m.group(3).split()[0]
        s = str(unit_qty) + unit_type
    
    return s


def split_unit(unit_text): 
    """
    Splits the normalized format of unit into (unit_qty, unit_type),
    with unit_type ∈ {"kg", "l", "stuk"}.
    """
    if not isinstance(unit_text, str) or not unit_text:
        return None, None
    
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", unit_text)
    if not m:
        print("[WARN] cannot parse:", unit_text)
        return None, None
    
    unit_qty = float(m.group(1))   
    unit_type = m.group(2)

    if unit_type in ("g","gram", "gr"):
        return unit_qty / 1000.0, "kg"
    if unit_type in ("kg", "kilo"):
        return unit_qty, "kg"
    if unit_type == "ml":
        return unit_qty / 1000.0, "l"
    if unit_type == "cl":
        return unit_qty / 100.0, "l"
    if unit_type in ("l", "liter"):
        return unit_qty, "l"    
    
    return unit_qty, "stuk"


def split_missing_unit(table: str):
    """
    Split unit_du only for rows where unit_qty or unit_type_du is NULL
    """
    supabase = get_supabase()

    resp = (
        supabase.table(table)
        .select("sku, unit_du")
        .is_("unit_type_du", None)
        .execute()
    )

    rows = resp.data or []
    if not rows:
        print(f"[split unit] {table}: no unit to parse")
        return

    updates = []
    for r in rows:
        unit_normalized = normalize_unit(r["unit_du"])
        unit_qty, unit_type_du = split_unit(unit_normalized)
        if unit_qty is not None and unit_type_du is not None:
            updates.append(
                {
                    "sku": r["sku"],
                    "unit_qty": unit_qty,
                    "unit_type_du": unit_type_du
                }
            )

    if updates:
        upsert_rows(table, updates, conflict_col="sku")
        print(f"[unit split] {table}: split {len(updates)} rows")


