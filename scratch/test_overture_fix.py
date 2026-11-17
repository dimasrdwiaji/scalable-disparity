import duckdb
from pathlib import Path

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
bbox = (106.82, -6.18, 106.83, -6.17)
out_amenities = Path("scratch/test_amenities.parquet")
out_transport = Path("scratch/test_transport.parquet")

print("Testing fixed Overture Amenities query...")
q_amenities = f"""
COPY (
    SELECT 
        id, 
        names.primary AS name, 
        taxonomy.primary AS category,
        geometry
    FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
    WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
      AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
      AND (
          taxonomy.primary IN (
              'school', 'hospital', 'clinic', 'supermarket', 'grocery_store',
              'education.school', 'healthcare.hospital', 'healthcare.clinic', 'commercial.supermarket_grocery'
          )
          OR basic_category IN ('school', 'hospital', 'clinic', 'supermarket', 'grocery_store')
      )
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
) TO '{out_amenities.as_posix()}' (FORMAT PARQUET);
"""
con.execute(q_amenities)
count_a = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_amenities.as_posix()}')").fetchone()[0]
print(f"Amenities query succeeded! Extracted {count_a} records.")

print("Testing fixed Overture Transportation query...")
q_transport = f"""
COPY (
    SELECT 
        id, 
        class, 
        subtype,
        geometry
    FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=transportation/type=segment/*', hive_partitioning=true)
    WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
      AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
      AND (subtype IS NULL OR subtype != 'rail')
) TO '{out_transport.as_posix()}' (FORMAT PARQUET);
"""
con.execute(q_transport)
count_t = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_transport.as_posix()}')").fetchone()[0]
print(f"Transportation query succeeded! Extracted {count_t} records.")
