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
        f"../../20_intermediate_data/nc_dislocation_"
        f"{SAMPLE_PCT:.2f}_sample_map{year}_party.geojson"
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
            "dem",
            "knn_shr_dem",
            "district_dem_share",
            "partisan_dislocation",
            "district",
            "abs_partisan_dislocation",
            "map",
        ]
    ]
    voters.append(piedmont_voters)

piedmont_voters = pd.concat(voters)

piedmont_voters[piedmont_voters["dem"] == 1]

dislocation[2024]
#########
# Plot Kernel Densities by Map
#########
piedmont_voters["Map"] = "2022 Map"
piedmont_voters.loc[piedmont_voters["map"] == 2024, "Map"] = "2024 Map"

import matplotlib.pyplot as plt

for i in ["partisan_dislocation", "abs_partisan_dislocation"]:
    f = plt.figure()
    if i == "abs_partisan_dislocation":
        abs_string = " Absolute"
    else:
        abs_string = ""
    (
        so.Plot(
            piedmont_voters[[i, "Map"]],
            x=i,
            color="Map",
        )
        .add(so.Area(), so.KDE(bw_adjust=2, common_norm=True, common_grid=True))
        .label(
            title=f"Distribution of{abs_string} Partisan Dislocation for Democrats by Map",
            y="Share of Voters",
            x=f"Voter{abs_string} Partisan Dislocation Score",
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
        f"Distribution of Partisan{abs_string} Dislocation across Democratic Voters in the Piedmont Triad Combined Statistical Area (CSA).",
        horizontalalignment="center",
        wrap=True,
        fontsize=10,
    )

    f.savefig(f"../../30_results/piedmont_triad_{i}_densities_party.png")

#############
# Measure individual-level change
#############

mergable = dict()
for year in [2022, 2024]:
    for_merge = gpd.overlay(dislocation[year], piedmont)
    mergable[year] = for_merge[
        ["dem", "abs_partisan_dislocation", "partisan_dislocation"]
    ].rename(
        columns={
            "partisan_dislocation": f"partisan_dislocation_{year}",
            "abs_partisan_dislocation": f"abs_partisan_dislocation_{year}",
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
assert (voters_wide.dem_x == voters_wide.dem_y).all()

voters_wide["change_abs_dislocation"] = (
    voters_wide[f"abs_partisan_dislocation_{2024}"]
    - voters_wide[f"abs_partisan_dislocation_{2022}"]
)


f = plt.figure()
(
    so.Plot(
        voters_wide.loc[voters_wide["dem_x"] == 1, ["change_abs_dislocation"]],
        x="change_abs_dislocation",
    )
    .add(so.Area(), so.KDE(bw_adjust=2))
    .label(
        title="Individual-Level Change in Absolute Dislocation for Democrats\nIn Piedmont Triad",
        y="Share of Voters",
        x="Individual-Level Change in Absolute Dislocation from 2022 Map to 2024 Map",
    )
    .theme({**style.library["seaborn-v0_8-whitegrid"]})
    .layout(extent=(0.1, 0.2, 0.9, 0.8))
    .on(f)
    .show()
)
ax = f.axes[0]
ax.axvline(x=0, ymin=0, color="grey")
ax.axvline(
    x=voters_wide.loc[voters_wide["dem_x"] == 1, "change_abs_dislocation"].mean(),
    ymin=0,
    color="red",
    linestyle="dashed",
)
ax.axvline(
    x=voters_wide.loc[voters_wide["dem_x"] == 1, "change_abs_dislocation"].median(),
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
f.savefig("../../30_results/piedmont_triad_change_party.png")
