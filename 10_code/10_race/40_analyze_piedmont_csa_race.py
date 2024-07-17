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

dislocation = dict()

# Get data

for year in [2022, 2024]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)

# Get piedmont
csas = gpd.read_file("../../00_source_data/csa_2020/US_csa_2020.shp").to_crs(epsg=PROJ)
piedmont_shape = csas[csas["NAME"] == "Greensboro--Winston-Salem--High Point, NC"]

# get Charlotte (csa wanders into SC, so need to clip)
charlotte_concord_shape = csas[csas["NAME"] == "Charlotte-Concord, NC-SC"]
states = gpd.read_file("../../00_source_data/states_2020/US_state_2022.shp").to_crs(
    epsg=PROJ
)
nc = states[states["NAME"] == "North Carolina"]
charlotte_shape = charlotte_concord_shape.clip(nc)


# Sanity Check
fig, ax = plt.subplots()
nc.plot(ax=ax, color="blue", alpha=0.7)
piedmont_shape.plot(ax=ax, color="red", alpha=0.7)
charlotte_shape.plot(ax=ax, color="green", alpha=0.7)
fig

###########
# Key Params for figures
###########

racial_groups = {0: "Not Any Part Black", 1: "Any Part Black"}
csas = [
    {
        "short": "piedmont",
        "long": "Piedmont Triad",
        "formal": "Greensboro--Winston-Salem--High Point Combined Statistical Area",
        "shp": piedmont_shape,
        "limits_two": (-0.17, 0.15),
        "limits_change": (-0.23, 0.15),
    },
    {
        "short": "charlotte",
        "long": "Charlotte-Concord CSA",
        "formal": "North Carolina subset of the Charlotte-Concord Combined Statistical Area",
        "shp": charlotte_shape,
        "limits_two": (-0.23, 0.21),
        "limits_change": (-0.3, 0.28),
    },
]

########
# Plot Dislocation Histograms by Map
########


def plot_kdensities_diff_maps(area_dict, race_key):
    voters = list()
    for year in [2022, 2024]:
        one_year_voters = gpd.overlay(dislocation[year], area_dict["shp"])
        one_year_voters = one_year_voters[
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
        voters.append(one_year_voters)

    voter_subset = pd.concat(voters)

    voter_subset = voter_subset[voter_subset["ap_black"] == race_key]

    # Plot Kernel Densities by Map
    voter_subset["Map"] = "2022 Map"
    voter_subset.loc[voter_subset["map"] == 2024, "Map"] = "2024 Map"

    obs = len(voter_subset)
    f = plt.figure()
    (
        so.Plot(
            voter_subset[["racial_dislocation", "Map"]],
            x="racial_dislocation",
            color="Map",
        )
        .add(so.Area(), so.KDE(bw_adjust=2, common_norm=True, common_grid=True))
        .label(
            title=f"Racial Dislocation for {racial_groups[race_key]} VAP\nin {area_dict['long']} by Map",
            y=f"Share of {racial_groups[race_key]} VAP",
            x="VAP Racial Dislocation Score",
        )
        .limit(x=area_dict["limits_two"])
        .theme(nick_theme)
        .layout(extent=(0.1, 0.2, 0.9, 0.8))
        .on(f)
        .show()
    )

    ax = f.axes[0]
    ax.axvline(x=0, ymin=0, color="grey")
    ax.axvline(
        x=voter_subset.loc[
            (voter_subset["ap_black"] == race_key) & (voter_subset["map"] == 2022),
            "racial_dislocation",
        ].mean(),
        ymin=0,
        color="blue",
        linestyle="dashed",
    )
    ax.axvline(
        x=voter_subset.loc[
            (voter_subset["ap_black"] == race_key) & (voter_subset["map"] == 2024),
            "racial_dislocation",
        ].mean(),
        ymin=0,
        color="orange",
        linestyle="dotted",
    )

    ax.yaxis.set_ticks([])
    # ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.05))
    f.text(
        0.50,
        0.02,
        f"Distribution of Racial Dislocation across {racial_groups[race_key]} VAP in the {area_dict['formal']} (CSA)."
        " Negative values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood."
        " Average value for 2022 indicated with dashed blue line, average value for 2024 indicated with dotted orange line.",
        horizontalalignment="center",
        wrap=True,
        fontsize=8,
    )

    f.savefig(
        f"../../30_results/dislocation_densities_race_apblack{race_key}_{area_dict['short']}.png"
    )


for area in csas:
    for race in racial_groups.keys():
        plot_kdensities_diff_maps(area, race)


#############
# Measure individual-level change
#############


def plot_change_by_map(area_dict, race_key):

    mergable = dict()
    for year in [2022, 2024]:
        for_merge = gpd.overlay(dislocation[year], area_dict["shp"])
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

    avg_change = voters_wide.loc[
        voters_wide["ap_black_x"] == race_key, "change_racial_dislocation"
    ].mean()

    f = plt.figure()
    (
        so.Plot(
            voters_wide.loc[
                voters_wide["ap_black_x"] == race_key, ["change_racial_dislocation"]
            ],
            x="change_racial_dislocation",
        )
        .add(so.Area(), so.KDE(bw_adjust=2))
        .label(
            title=f"Individual-Level Change in Racial Dislocation\n"
            f"for {racial_groups[race_key]} VAP in {area_dict['long']}."
            f"\nAverage Change: {avg_change:.2f}",
            y=f"Share of {racial_groups[race_key]} VAP",
            x="Individual-Level Change in Racial Dislocation from 2022 Map to 2024 Map",
        )
        .theme(nick_theme)
        .layout(extent=(0.1, 0.2, 0.9, 0.8))
        .on(f)
        .show()
    )
    ax = f.axes[0]
    ax.yaxis.set_ticks([])
    ax.axvline(x=0, ymin=0, color="grey")
    ax.axvline(
        x=avg_change,
        ymin=0,
        color="red",
        linestyle="dashed",
    )
    ax.yaxis.set_ticks([])
    f.text(
        0.50,
        0.02,
        f"Distribution of individual-level change in Racial Dislocation for {racial_groups[race_key]} VAP in {area_dict['formal']} (CSA)."
        " Negative values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood."
        f" Average change indicated with red dashed line.",
        horizontalalignment="center",
        wrap=True,
        fontsize=7,
    )

    f.savefig(
        f"../../30_results/distribution_change_race_apblack{race_key}_{area_dict['short']}.png"
    )


for area in csas:
    for race in racial_groups.keys():
        plot_change_by_map(area, race)
