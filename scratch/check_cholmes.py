import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

cholmes_urls = [
    "s3://us-west-2.opendata.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/country_iso=IDN/*.parquet",
    "s3://us-west-2.opendata.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/country_iso=IDN/IDN.parquet",
    "s3://us-west-2.opendata.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/IDN.parquet",
    "s3://us-west-2.opendata.source.coop/cholmes/google-open-buildings/v3/geoparquet-by-country/IDN/*.parquet",
]

for u in cholmes_urls:
    print(f"\nTrying: {u}")
    try:
        df = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{u}') LIMIT 1;").df()
        print("Found cholmes!")
        print(df[["column_name", "column_type"]])
        break
    except Exception as e:
        print("Failed:", type(e), e)
