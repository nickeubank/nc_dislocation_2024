import geopandas as gpd
import pandas as pd
import numpy as np
import partisan_dislocation as pdn
import time

SAMPLE_PCT = 0.03
PROJ = 32119

pd.set_option("mode.copy_on_write", True)

vtds = gpd.read_file(
    "../../00_source_data/election_data/nc_gen_20_prec/nc_gen_20_st_sldu_prec.shp"
).to_crs(epsg=PROJ)

#############
# Vote Counts
#############

vtds = vtds[
    [
        "UNIQUE_ID",
        "COUNTYFP",
        "ENR_DESC",
        "COUNTY_NAM",
        "COUNTY_ID",
        "SLDU_DIST",
        "G20PRERTRU",
        "G20PREDBID",
        "G20PRELJOR",
        "G20PREGHAW",
        "G20PRECBLA",
        "G20PREOWRI",
        "G20USSRTIL",
        "G20USSDCUN",
        "G20USSLBRA",
        "G20USSCHAY",
        "G20GOVRFOR",
        "G20GOVDCOO",
        "G20GOVLDIF",
        "G20GOVCPIS",
        "G20LTGRROB",
        "G20LTGDHOL",
        "G20ATGRONE",
        "G20ATGDSTE",
        "G20TRERFOL",
        "G20TREDCHA",
        "G20SOSRSYK",
        "G20SOSDMAR",
        "G20AUDRSTR",
        "G20AUDDWOO",
        "G20AGRRTRO",
        "G20AGRDWAD",
        "G20INSRCAU",
        "G20INSDGOO",
        "G20LABRDOB",
        "G20LABDHOL",
        "G20SPIRTRU",
        "G20SPIDMAN",
        "G20SSCRNEW",
        "G20SSCDBEA",
        "G20SSCRBER",
        "G20SSCDINM",
        "G20SSCRBAR",
        "G20SSCDDAV",
        "G20SACRWOO",
        "G20SACDSHI",
        "G20SACRGOR",
        "G20SACDCUB",
        "G20SACRDIL",
        "G20SACDSTY",
        "G20SACRCAR",
        "G20SACDYOU",
        "G20SACRGRI",
        "G20SACDBRO",
        "geometry",
    ]
]

vtds["dem"] = vtds["G20PREDBID"]
vtds["rep"] = vtds["G20PRERTRU"]

#########
# Points in Polygons
#########


print(f"Starting points in polygons, pct {SAMPLE_PCT:.3f}")
start_time = time.time()

voters = pdn.random_points_in_polygon(
    vtds, p=SAMPLE_PCT, dem_vote_count="dem", repub_vote_count="rep"
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
knn.to_file(f"../../20_intermediate_data/nc_knn_{SAMPLE_PCT:.2f}_sample_party.geojson")

print("Done with KNN")
