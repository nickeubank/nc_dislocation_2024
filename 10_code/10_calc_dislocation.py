import geopandas as gpd
import pandas as pd
import numpy as np
import partisan_dislocation as pdn

pd.set_option("mode.copy_on_write", True)

############
# Load districts and voters
############
SAMPLE_PCT = 0.01
PROJ = 32119

dists = dict()

for year in [2022, 2024]:
    dists[year] = gpd.read_file(
        f"../00_source_data/district-shapes_{i}/district-shapes/POLYGON.shp"
    ).to_crs(epsg=PROJ)
    print(len(dists[year]))

knn = gpd.read_file(
    f"../20_intermediate_data/nc_knn_{SAMPLE_PCT:.2f}_sample.geojson"
).to_crs(epsg=PROJ)

# Sanity checks
assert knn.dem.mean() < 0.25
assert 0.15 < knn.dem.mean()

#########
# Get Dislocation Scores
#########

dislocation_points = dict()
for year in [2022, 2024]:
    temp_df = pdn.calculate_dislocation(
        knn,
        dists[year],
        knn_column="knn_shr_dem",
        dem_column="dem",
        district_id_col="NAME",
    )
    temp_df["abs_partisan_dislocation"] = np.abs(temp_df["partisan_dislocation"])

    # Make names more accurate for racial use case
    temp_df = temp_df.rename(
        columns={
            "knn_shr_dem": "knn_shr_ap_black",
            "dem": "ap_black",
            "partisan_dislocation": "racial_dislocation",
            "abs_partisan_dislocation": "abs_racial_dislocation",
            "NAME": "district",
        }
    )
    temp_df["map"] = year
    temp_df = temp_df.to_crs(epsg=4326)
    temp_df.to_file(
        f"../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}.geojson"
    )
