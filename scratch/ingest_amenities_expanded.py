import time
from pathlib import Path
import duckdb

raw_dir = Path("data/raw")
out_path = raw_dir / "overture_amenities.parquet"
out_str = out_path.as_posix()

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.install_extension("httpfs")
con.load_extension("httpfs")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")
con.execute("SET http_retries = 5;")
con.execute("SET http_timeout = 60000;")

bbox = (106.35, -6.75, 107.65, -5.95)
release = "2026-10-21.0"

cats = [
    'convenience_store', 'grocery_store', 'supermarket', 'shopping',
    'clothing_store', 'marketplace', 'kiosk', 'general_store', 'department_store',
    'shopping_mall', 'bakery', 'commercial.supermarket_grocery',
    'restaurant', 'indonesian_restaurant', 'fast_food_restaurant', 'cafe',
    'coffee_shop', 'food_court', 'chicken_restaurant', 'asian_restaurant',
    'hospital', 'clinic', 'pharmacy', 'dentist', 'bank_or_credit_union', 'atm',
    'post_office', 'government_office', 'social_or_community_service',
    'healthcare.hospital', 'healthcare.clinic',
    'school', 'elementary_school', 'preschool', 'college_university', 'education',
    'education.school',
    'muslim_place_of_worship', 'christian_place_of_worship', 'place_of_worship',
    'hindu_temple', 'buddhist_temple', 'church', 'mosque', 'temple', 'synagogue',
    'religious_organization',
]
cat_str = ", ".join(f"'{c}'" for c in cats)

query = f"""
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            coalesce(taxonomy.primary, basic_category) AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND coalesce(taxonomy.primary, basic_category) IN ({cat_str})
        UNION ALL
        SELECT 
            id, 
            names.primary AS name, 
            subtype AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{out_str}' (FORMAT PARQUET);
"""

print("Executing DuckDB S3 query for expanded amenities...")
t0 = time.time()
con.execute(query)
count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_str}')").fetchone()[0]
print(f"Ingested {count} expanded amenities in {time.time()-t0:.2f} seconds!")
print(f"File size: {out_path.stat().st_size / 1024 / 1024:.2f} MB")
