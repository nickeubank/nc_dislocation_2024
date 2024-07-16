import pandas as pd
import numpy as np
import geopandas as gpd
import seaborn.objects as so
import seaborn as sns
from matplotlib import style
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

pd.set_option("mode.copy_on_write", True)

SAMPLE_PCT = 0.02
PROJ = 32119

dislocation = dict()

# Get data

for year in [2022, 2024]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)

csa = gpd.read_file("../../00_source_data/csa_2020/US_csa_2020.shp").to_crs(epsg=PROJ)
piedmont = csa[csa["NAME"] == "Greensboro--Winston-Salem--High Point, NC"]


# Sanity Check
piedmont.plot()

# Subset for voters in CSA
voters = list()
for year in [2022, 2024]:
    piedmont_voters = gpd.overlay(dislocation[year], piedmont)
    piedmont_voters = piedmont_voters[
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
    voters.append(piedmont_voters)

piedmont_voters = pd.concat(voters)

piedmont_voters[piedmont_voters["ap_black"] == 1]

#########
# Plot Kernel Densities by Map
#########
piedmont_voters["Map"] = "2022 Map"
piedmont_voters.loc[piedmont_voters["map"] == 2024, "Map"] = "2024 Map"


#
# piedmont_voters.loc[piedmont_voters["Map"] == "2022 Map", "racial_dislocation"].plot.density(bw_method=0.3,ax=ax)

import matplotlib.pyplot as plt


f = plt.figure()
(
    so.Plot(
        piedmont_voters[["racial_dislocation", "Map"]],
        x="racial_dislocation",
        color="Map",
    )
    .add(so.Area(), so.KDE(bw_adjust=2, common_norm=True, common_grid=True))
    .label(
        title="Distribution of Racial Dislocation for AP Black VAP by Map",
        y="Share of VAP",
        x="VAP Racial Dislocation Score",
    )
    .theme({**style.library["seaborn-v0_8-whitegrid"]})
    .layout(extent=(0.1, 0.2, 0.9, 0.8))
    .on(f)
    .show()
)
ax = f.axes[0]
ax.axvline(x=0, ymin=0, color="red")
ax.yaxis.set_ticks([])
# ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.05))
f.text(
    0.50,
    0.02,
    "Distribution of Racial Dislocation across Any Part Black VAP in the Piedmont Triad Combined Statistical Area (CSA)."
    " Negative values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood."
    " In other words, negative values correspond to racial dilution.",
    horizontalalignment="center",
    wrap=True,
    fontsize=8,
)

f.savefig("../../30_results/piedmont_triad_dislocation_densities_race.png")


#############
# Measure individual-level change
#############

mergable = dict()
for year in [2022, 2024]:
    for_merge = gpd.overlay(dislocation[year], piedmont)
    mergable[year] = for_merge[
        ["ap_black", "abs_racial_dislocation", "racial_dislocation"]
    ].rename(
        columns={
            "racial_dislocation": f"racial_dislocation_{year}",
            "abs_racial_dislocation": f"abs_racial_dislocation_{year}",
        }
    )

voters_wide = pd.merge(
    mergable[2022],
    mergable[2024],
    left_index=True,
    right_index=True,
    how="outer",
    validate="1:1",
    indicator=True,
)
assert (voters_wide._merge == "both").all()
assert len(mergable[2022]) == len(voters_wide)
assert (voters_wide["ap_black_x"] == voters_wide["ap_black_y"]).all()

voters_wide["change_racial_dislocation"] = (
    voters_wide[f"racial_dislocation_{2024}"]
    - voters_wide[f"racial_dislocation_{2022}"]
)

f = plt.figure()
(
    so.Plot(
        voters_wide.loc[voters_wide["ap_black_x"] == 1, ["change_racial_dislocation"]],
        x="change_racial_dislocation",
    )
    .add(so.Area(), so.KDE(bw_adjust=2))
    .label(
        title="Individual-Level Change in Racial Dislocation for AP Black VAP\nIn Piedmont Triad",
        y="Share of VAP",
        x="Individual-Level Change in Racial Dislocation from 2022 Map to 2024 Map",
    )
    .theme({**style.library["seaborn-v0_8-whitegrid"]})
    .layout(extent=(0.1, 0.2, 0.9, 0.8))
    .on(f)
    .show()
)
ax = f.axes[0]
ax.yaxis.set_ticks([])
ax.axvline(x=0, ymin=0, color="grey")
ax.axvline(
    x=voters_wide.loc[
        voters_wide["ap_black_x"] == 1, "change_racial_dislocation"
    ].mean(),
    ymin=0,
    color="red",
    linestyle="dashed",
)
ax.axvline(
    x=voters_wide.loc[
        voters_wide["ap_black_x"] == 1, "change_racial_dislocation"
    ].median(),
    ymin=0,
    color="blue",
    linestyle="dashed",
)
ax.yaxis.set_ticks([])
f.text(
    0.50,
    0.02,
    f"0 marked in grey, mean in red, and median in blue.",
    horizontalalignment="center",
    wrap=True,
    fontsize=10,
)


f.savefig("../../30_results/piedmont_triad_change_race.png")
