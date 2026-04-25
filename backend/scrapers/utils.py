from datetime import date, datetime

def normalize_date(v):
    """Convert date/datetime to YYYY-MM-DD string; keep None as None."""
    if v is None:
        return None
    
    # If it's a datetime or date object, extract just the date part
    if isinstance(v, (date, datetime)):
        # .strftime('%Y-%m-%d') works for both date and datetime
        return v.strftime('%Y-%m-%d')
    
    # If it's already a string, we take the first 10 characters (the date)
    # This handles "2049-12-31T23:59:59..." -> "2049-12-31"
    str_v = str(v)
    if len(str_v) >= 10 and str_v[4] == '-' and str_v[7] == '-':
        return str_v[:10]
        
    return str_v

def normalize_price(v):
    """
    Normalize price to float or None for comparison.
    - In scrapper: current_price = f"0.{price_large_tag.get_text(strip=True)}". This is a string.
    - In supabse: current_price is stored as float8
    - To compare them, we need to normalize into float. 
    """
    if v is None:
        return None
    return float(v) 
    