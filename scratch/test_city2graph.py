import geopandas as gpd
import pandas as pd
import h3
from shapely.geometry import Point
from city2graph.utils.spatial import create_isochrone
from phys_living_index.features.residential import population_density, residential_mask

pop = pd.read_parquet("data/interim/layers/population.parquet")
bldg = pd.read_parquet("data/interim/layers/buildings.parquet")
acc = pd.read_parquet("data/interim/layers/accessibility.parquet")

density = population_density(pop["population"])
is_res = residential_mask(density, bldg["building_count"], min_density_per_km2=300.0, min_building_count=1)

# Find residential cells with 0 amenities in accessibility.parquet
res_zero = acc[is_res & (acc["amenities_15m"] == 0)]
print(f"Residential cells with 0 amenities: {len(res_zero)}")
print("Sample residential cells with 0 amenities:")
sample_zeros = res_zero.head(5)
for cell, row in sample_zeros.iterrows():
    lat, lon = h3.cell_to_latlng(cell)
    print(f"Cell {cell}: lat={lat:.4f}, lon={lon:.4f}, snap_dist={row['snap_distance_m']:.1f}m, pop={pop.loc[cell, 'population']:.0f}, bldgs={bldg.loc[cell, 'building_count']:.0f}")

# Also check Monas & BSD cells
monas_cell = h3.latlng_to_cell(-6.1754, 106.8272, 8)
bsd_cell = h3.latlng_to_cell(-6.3070, 106.6500, 8)
sampora_cell = h3.latlng_to_cell(-6.3110, 106.6450, 8)

for name, cell in [("Monas (CBD)", monas_cell), ("BSD Central", bsd_cell), ("Kampung Sampora", sampora_cell)]:
    if cell in acc.index:
        row = acc.loc[cell]
        print(f"\n{name} ({cell}):")
        print(f"  amenities_15m: {row['amenities_15m']}")
        print(f"  snap_distance_m: {row['snap_distance_m']:.1f}m")
        print(f"  pop: {pop.loc[cell, 'population']:.0f}")
        print(f"  bldgs: {bldg.loc[cell, 'building_count']:.0f}")
