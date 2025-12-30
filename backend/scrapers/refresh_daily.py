from concurrent.futures import ThreadPoolExecutor, as_completed


from hoogvliet_core import refresh_hoogvliet_daily
from dirk_core import refresh_dirk_daily
from ah_core import refresh_ah_daily

from processors.translate_products import translate_missing_product_names
from processors.normalize_products import split_missing_unit
from processors.embed_products import embed_missing_products

PIPELINES = {
    "ah": refresh_ah_daily,
    "dirk": refresh_dirk_daily,
    "hoogvliet": refresh_hoogvliet_daily,
}

def run_pipeline(name: str, refresh_func):
    print(f"[{name}] pipeline start")

    # 1. refresh raw data
    refresh_func()
    print(f"[{name}] refresh done")

    # 2. translate
    translate_missing_product_names(name)
    print(f"[{name}] translate done")

    # 3. split
    split_missing_unit(name)
    print(f"[{name}] split done")

    # 3. embed
    embed_missing_products(name)
    print(f"[{name}] embed done")

    print(f"[{name}] pipeline finished")


def main():
    print("=== Start daily refresh pipelines (parallel by supermarket) ===")

    results = {}

    with ThreadPoolExecutor(max_workers=len(PIPELINES)) as executor:
        future_to_name = {
            executor.submit(run_pipeline, name, refresh_func): name
            for name, refresh_func in PIPELINES.items()
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                future.result()
                results[name] = "ok"
                print(f"[OK] {name} pipeline completed")
            except Exception as e:
                results[name] = f"error: {e}"
                print(f"[ERROR] {name} pipeline failed: {e}")

    print("=== All pipelines finished ===")
    print("Summary:", results)


if __name__ == "__main__":
    main()
