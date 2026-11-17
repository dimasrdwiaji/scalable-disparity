from pathlib import Path

path = Path("scripts/run_ingestion.py")
text = path.read_text(encoding="utf-8")

old_in = """              coalesce(taxonomy.primary, basic_category) IN (
                  'school', 'hospital', 'clinic', 'supermarket', 'grocery_store',
                  'education.school', 'healthcare.hospital', 'healthcare.clinic', 'commercial.supermarket_grocery'
              )"""

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

new_in = f"""              coalesce(taxonomy.primary, basic_category) IN (
                  {cat_str}
              )"""

text = text.replace(old_in, new_in)
path.write_text(text, encoding="utf-8")
print("Updated scripts/run_ingestion.py successfully!")
