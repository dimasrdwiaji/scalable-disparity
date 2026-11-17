import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")
con.execute("SET allow_asterisks_in_http_paths = true;")

urls_to_try = [
    "https://data.source.coop/vida/google-microsoft-osm-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*.parquet",
    "https://data.source.coop/vida/google-microsoft-osm-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*",
    "s3://us-west-2.opendata.source.coop/vida/google-microsoft-osm-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*.parquet",
    "https://data.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/country_iso=IDN/IDN.parquet",
    "https://data.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/country_iso=IDN/*.parquet",
]

for u in urls_to_try:
    print(f"\nTrying URL: {u}")
    try:
        df = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{u}') LIMIT 1;").df()
        print("SUCCESS! Columns:")
        print(df[["column_name", "column_type"]])
        break
    except Exception as e:
        print("Failed:", type(e), e)
