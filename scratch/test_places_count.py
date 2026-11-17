import time
import duckdb

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

categories = [
    # Daily retail, markets, sembako, shops
    "convenience_store", "grocery_store", "supermarket", "shopping",
    "clothing_store", "marketplace", "kiosk", "general_store", "department_store",
    "shopping_mall", "bakery",
    # Food, warung, restaurants, warkop
    "restaurant", "indonesian_restaurant", "fast_food_restaurant", "cafe",
    "coffee_shop", "food_court", "chicken_restaurant", "asian_restaurant",
    # Healthcare & daily essentials
    "hospital", "clinic", "pharmacy", "dentist", "bank_or_credit_union", "atm",
    "post_office", "government_office", "social_or_community_service",
    # Education
    "school", "elementary_school", "preschool", "college_university", "education",
    # ALL Places of worship (Muslim, Christian, Hindu, Buddhist, generic)
    "muslim_place_of_worship", "christian_place_of_worship", "place_of_worship",
    "hindu_temple", "buddhist_temple", "church", "mosque", "temple", "synagogue",
    "religious_organization"
]

cat_str = ", ".join(f"'{c}'" for c in categories)

query = f"""
    SELECT COUNT(*) as total_count
    FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
    WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
      AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
      AND coalesce(taxonomy.primary, basic_category) IN ({cat_str})
"""

t0 = time.time()
res = con.execute(query).df()
print("Query result:")
print(res)
print(f"Time taken: {time.time()-t0:.2f}s")
