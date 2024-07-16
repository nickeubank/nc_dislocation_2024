import pandas as pd
import numpy as np
import geopandas as gpd
import partisan_dislocation as pdn

pd.set_option("mode.copy_on_write", True)

#########
# Load
#########

SAMPLE_PCT = 0.03
PROJ = 32119

dislocation = dict()
dists = dict()

for year in [2022, 2024]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)

    dists[year] = (
        gpd.read_file(
            f"../../00_source_data/district-shapes_{year}/district-shapes/POLYGON.shp"
        )
        .to_crs(epsg=PROJ)
        .rename(columns={"NAME": "district"})
    )

piedmonts = ((385_000, 600_000), (100_000, 325_000))

##########
# Plot minority only, signed
##########
plots = pdn.plot_dislocation_points(
    dislocation,
    dists,
    id_col="ap_black",
    id_col_label_text="Any Part Black",
    dislocation_col="racial_dislocation",
    dislocation_label_text="Racial Dislocation",
    map_limits=piedmonts,
    minority_sample_frac=1,
    majority_sample_frac=0.2,
    minority_only=1,
    axis_labels=False,
)

for p in plots.keys():
    plots[p].figure.savefig(
        f"../../30_results/{p}_signed_dislocation_piedmont_minorityonly_race.png"
    )
