import geopandas as gpd
import pandas as pd
import numpy as np
import partisan_dislocation as pdn
import time

pd.set_option("mode.copy_on_write", True)

blocks = gpd.read_file("../00_source_data/nhgis_blocks_2020/nc_block_2020.shp")
block_data = pd.read_csv(
    "../00_source_data/nhgis_blocks_2020/nhgis_ds248_2020_block.csv"
)

blocks = pd.merge(
    blocks, block_data, on="GISJOIN", how="left", validate="1:1", indicator=True
)
assert (blocks._merge == "both").all()

# Calculate any part black
black_cols = [
    "U7D004",
    "U7D011",
    "U7D016",
    "U7D017",
    "U7D018",
    "U7D019",
    "U7D027",
    "U7D028",
    "U7D029",
    "U7D030",
    "U7D037",
    "U7D038",
    "U7D039",
    "U7D040",
    "U7D041",
    "U7D042",
    "U7D048",
    "U7D049",
    "U7D050",
    "U7D051",
    "U7D052",
    "U7D053",
    "U7D058",
    "U7D059",
    "U7D060",
    "U7D061",
    "U7D064",
    "U7D065",
    "U7D066",
    "U7D067",
    "U7D069",
    "U7D071",
]

blocks["ap_black"] = blocks[black_cols].sum(axis="columns")
blocks["total_pop"] = blocks["U7D001"]
blocks["not_ap_black"] = blocks["total_pop"] - blocks["ap_black"]
blocks["share_ap_black"] = blocks["ap_black"] / blocks["total_pop"]

# Sanity checks
blocks.plot("share_ap_black", cmap="Reds", legend=True)

#########
# Points in Polygons
#########

SAMPLE_PCT = 0.05

print(f"Starting points in polygons, pct {SAMPLE_PCT:.3f}")
start_time = time.time()

blocks = blocks.to_crs(epsg=32119)
voters = pdn.random_points_in_polygon(
    blocks, p=SAMPLE_PCT, dem_vote_count="ap_black", repub_vote_count="not_ap_black"
)

print("Done with points in polygons")
print(
    f"Total Running time for {SAMPLE_PCT:.2f}:"
    f" {(time.time() - start_time) /  60:.1f} minutes"
)

# Sanity check
voters.plot("dem", cmap="RdBu", markersize=0.1, alpha=0.5, figsize=(8, 8), legend=True)

########
# KNN
########
NUM_DISTRICTS = 14
knn = pdn.calculate_voter_knn(
    voters, k=len(voters) / NUM_DISTRICTS, target_column="dem"
)
knn = knn.to_crs(epsg=4326)
knn.to_file(f"../20_intermediate_data/nc_knn_{SAMPLE_PCT:.2f}_sample.geojson")

print("Done with KNN")
