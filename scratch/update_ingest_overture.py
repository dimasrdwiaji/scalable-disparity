from pathlib import Path

path = Path("src/phys_living_index/data/ingest_overture.py")
text = path.read_text(encoding="utf-8")

categories_code = '''OVERTURE_EXPANDED_AMENITY_CATEGORIES: list[str] = [
    # Daily retail, markets, sembako, shops
    "convenience_store", "grocery_store", "supermarket", "shopping",
    "clothing_store", "marketplace", "kiosk", "general_store", "department_store",
    "shopping_mall", "bakery", "commercial.supermarket_grocery",
    # Food, warung, restaurants, warkop
    "restaurant", "indonesian_restaurant", "fast_food_restaurant", "cafe",
    "coffee_shop", "food_court", "chicken_restaurant", "asian_restaurant",
    # Healthcare & daily essentials
    "hospital", "clinic", "pharmacy", "dentist", "bank_or_credit_union", "atm",
    "post_office", "government_office", "social_or_community_service",
    "healthcare.hospital", "healthcare.clinic",
    # Education
    "school", "elementary_school", "preschool", "college_university", "education",
    "education.school",
    # ALL Places of worship (Muslim, Christian, Hindu, Buddhist, generic)
    "muslim_place_of_worship", "christian_place_of_worship", "place_of_worship",
    "hindu_temple", "buddhist_temple", "church", "mosque", "temple", "synagogue",
    "religious_organization",
]
'''

if "OVERTURE_EXPANDED_AMENITY_CATEGORIES" not in text:
    text = text.replace(
        'DEFAULT_OVERTURE_RELEASE: str = "2026-10-21.0"\n',
        'DEFAULT_OVERTURE_RELEASE: str = "2026-10-21.0"\n\n' + categories_code
    )

old_query = """    return f\"\"\"
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            categories.main AS category,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND categories.main IN (
              'education.school', 'healthcare.hospital', 
              'healthcare.clinic', 'commercial.supermarket_grocery'
          )
        UNION ALL
        SELECT 
            id, 
            names.primary AS name, 
            subtype AS category,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{out_str}' (FORMAT PARQUET);
    \"\"\""""

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

new_query = f"""    return f\"\"\"
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            coalesce(taxonomy.primary, basic_category) AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{{release}}/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {{min_lon}} AND bbox.xmax <= {{max_lon}}
          AND bbox.ymin >= {{min_lat}} AND bbox.ymax <= {{max_lat}}
          AND coalesce(taxonomy.primary, basic_category) IN ({cat_str})
        UNION ALL
        SELECT 
            id, 
            names.primary AS name, 
            subtype AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{{release}}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {{min_lon}} AND bbox.xmax <= {{max_lon}}
          AND bbox.ymin >= {{min_lat}} AND bbox.ymax <= {{max_lat}}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{{out_str}}' (FORMAT PARQUET);
    \"\"\""""

text = text.replace(old_query, new_query)
path.write_text(text, encoding="utf-8")
print("Updated ingest_overture.py successfully!")
