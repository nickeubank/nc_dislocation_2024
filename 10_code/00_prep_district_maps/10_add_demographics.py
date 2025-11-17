import geopandas as gpd
import numpy as np
import pandas as pd
import partisan_dislocation as pdn

pd.set_option("mode.copy_on_write", True)

############
# Load districts and voters
############
PROJ = 32119

# Census blocks
blocks = gpd.read_file(
    "../../00_source_data/nhgis_blocks_2020_raceonly/nc_block_2020.shp"
).to_crs(PROJ)
block_data = pd.read_csv(
    "../../00_source_data/nhgis_blocks_2020_raceonly/nhgis_ds248_2020_block.csv"
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
blocks["vap"] = blocks["U7D001"]

blocks["centroid"] = blocks.geometry.centroid
blocks = blocks.set_geometry("centroid")
blocks = blocks[["centroid", "ap_black", "vap"]]


for year in [2022, 2024, 2025]:

    year = 2022
    dists = gpd.read_file(
        f"../../00_source_data/district-shapes_{year}/district-shapes/POLYGON.shp"
    ).to_crs(PROJ)
    assert len(dists) == 14

    dists = dists.rename(columns={"DISTRICT": "district", "NAME": "district"})

    blocks_w_dist = blocks.sjoin(dists[["geometry", "district"]], how="left")
    collapsed_blocks = blocks_w_dist.groupby("district")[["ap_black", "vap"]].sum()
    collapsed_blocks["pct_ap_black"] = (
        collapsed_blocks["ap_black"] / collapsed_blocks["vap"]
    )
    dists_w_race = pd.merge(
        dists,
        collapsed_blocks,
        on="district",
        how="outer",
        validate="1:1",
        indicator=True,
    )

    assert (dists_w_race._merge == "both").all()
    del dists_w_race["_merge"]

    if year != 2025:
        assert dists_w_race[["BlackPct", "pct_ap_black"]].corr().iloc[0, 0] > 0.99

    dists_w_race = dists_w_race.to_crs(epsg=4326)
    dists_w_race.to_file(f"../../20_intermediate_data/ncdistricts_{year}.geojson")
