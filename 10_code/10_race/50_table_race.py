import pandas as pd
import numpy as np
import geopandas as gpd
import seaborn.objects as so
import seaborn_objects_recipes as sor
from matplotlib import style
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
nick_theme = {**style.library["seaborn-v0_8-whitegrid"]}
nick_theme.update({"font.sans-serif": ["Fira Sans", "Arial", "sans-serif"]})

pd.set_option("mode.copy_on_write", True)

SAMPLE_PCT = 0.02
PROJ = 32119

# Get data
vap_list = list()
for year in [2022, 2024]:
    one_year_vap = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    )

    one_year_vap = one_year_vap[
        [
            "ap_black",
            "knn_shr_ap_black",
            "district_dem_share",
            "racial_dislocation",
            "district",
            "abs_racial_dislocation",
            "map",
        ]
    ]
    one_year_vap = pd.DataFrame(one_year_vap)

    vap_list.append(one_year_vap)

vap = pd.concat(vap_list)
tab = vap.groupby(["district", "ap_black", "map"], as_index=False)[
    "racial_dislocation"
].mean()

pivoted_table = pd.pivot(
    tab, columns=["map"], index=["district", "ap_black"], values="racial_dislocation"
).reset_index()
pivoted_table.columns.name = ""
pivoted_table["district"] = pivoted_table["district"].astype("int")
pivoted_table = pivoted_table.sort_values(["district", "ap_black"])
pivoted_table["change from 2022 to 2024"] = pivoted_table[2024] - pivoted_table[2022]
pivoted_table
