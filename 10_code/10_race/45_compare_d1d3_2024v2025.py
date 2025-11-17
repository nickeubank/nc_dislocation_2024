import warnings

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn.objects as so
import seaborn_objects_recipes as sor
from matplotlib import style
from matplotlib_inline.backend_inline import set_matplotlib_formats

warnings.simplefilter(action="ignore", category=FutureWarning)
set_matplotlib_formats("retina")
nick_theme = {**style.library["seaborn-v0_8-whitegrid"]}
nick_theme.update({"font.sans-serif": ["Fira Sans", "Arial", "sans-serif"]})

pd.set_option("mode.copy_on_write", True)

#########
# Load
#########

SAMPLE_PCT = 0.02
PROJ = 32119

dislocation = dict()
dists = dict()

for year in [2024, 2025]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)
    dislocation[year] = dislocation[year][dislocation[year].district.isin(["1", "3"])]
    print(year)
    # dislocation[year].plot()


# ###########
# # Key Params for figures
# ###########

racial_groups = {0: "Non-Black", 1: "Black"}

########
# Plot Dislocation Histograms by Map
########


def plot_kdensities_diff_maps(race_key):
    voters = list()
    for year in [2024, 2025]:
        one_year_voters = dislocation[year]
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
        one_year_voters["Map"] = f"{year} Map"
        voters.append(one_year_voters)

    voter_subset = pd.concat(voters)

    voter_subset = voter_subset[voter_subset["ap_black"] == race_key]

    obs = len(voter_subset)
    fig, ax = plt.subplots()
    (
        so.Plot(
            voter_subset[["racial_dislocation", "Map"]],
            x="racial_dislocation",
            color="Map",
        )
        .add(so.Area(), so.KDE(bw_adjust=2, common_norm=True, common_grid=True))
        .label(
            title=f"Racial Dislocation for {racial_groups[race_key]} VAP\nin Districts 1 and 3 by Map",
            y=f"Share of {racial_groups[race_key]} VAP",
            x=f"(Dilution){" "*20}VAP Racial Dislocation Score{" "*20}(Concentration)",
        )
        .limit(x=(-0.23, 0.21))
        .theme(nick_theme)
        .layout(extent=(0.1, 0.2, 0.90, 0.8))
        .on(ax)
        .plot()
    )

    ax.axvline(x=0, ymin=0, color="grey")

    means = dict()
    medians = dict()
    for i in [2024, 2025]:
        means[i] = voter_subset.loc[
            (voter_subset["ap_black"] == race_key) & (voter_subset["map"] == i),
            "racial_dislocation",
        ].mean()
        medians[i] = voter_subset.loc[
            (voter_subset["ap_black"] == race_key) & (voter_subset["map"] == i),
            "racial_dislocation",
        ].median()

    ax.axvline(
        x=means[2024],
        ymin=0,
        color="blue",
        linestyle="solid",
    )
    ax.text(
        means[2024],
        ax.get_ylim()[1] * 0.75,
        "Mean, 2024",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="blue",
        fontsize=8,
    )

    ax.axvline(
        x=means[2025],
        ymin=0,
        color="orange",
        linestyle="solid",
    )
    ax.text(
        means[2025],
        ax.get_ylim()[1] * 0.75,
        "Mean, 2025",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="orange",
        fontsize=8,
    )

    ax.axvline(
        x=medians[2024],
        ymin=0,
        color="blue",
        linestyle="dashed",
    )
    ax.text(
        medians[2024],
        ax.get_ylim()[1] * 0.85,
        "Median, 2024",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="blue",
        fontsize=8,
    )

    ax.axvline(
        x=medians[2025],
        ymin=0,
        color="orange",
        linestyle="dashed",
    )
    ax.text(
        medians[2025],
        ax.get_ylim()[1] * 0.85,
        "Median, 2025",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="orange",
        fontsize=8,
    )

    mean_change = (
        f"Avg Dislocation, 2024: {means[2024]:.3f}\n"
        f"Avg Dislocation, 2025: {means[2025]:.3f}"
    )

    median_change = (
        f"Median Dislocation, 2024: {medians[2024]:.3f}\n"
        f"Median Dislocation, 2025: {medians[2025]:.3f}"
    )

    # Add text in top right quadrant
    ax.text(
        0.044,
        4.1,
        mean_change,
        fontsize=8,
        verticalalignment="top",
        horizontalalignment="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    ax.text(
        0.044,
        3.5,
        median_change,
        fontsize=8,
        verticalalignment="top",
        horizontalalignment="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    # ax.yaxis.set_ticks([])
    ax.tick_params(axis="x", labelsize=8)
    fig.legends[0].set_bbox_to_anchor((0.9, 0.7))
    fig.text(
        0.05,
        0.02,
        f"Distribution of Racial Dislocation across {racial_groups[race_key]} VAP in the Districts 1 and 3."
        " Negative values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood."
        " Average values indicated with solid blue and orange lines, median values indicated with dashed lines.",
        horizontalalignment="left",
        wrap=True,
        fontsize=8,
    )

    fig.savefig(
        f"../../30_results/dislocation_densities_race_apblack{race_key}_d1d3.png",
        dpi=600,
        bbox_inches="tight",
    )


for i in [0, 1]:
    plot_kdensities_diff_maps(i)

#############
# Measure individual-level change
#############


def plot_change_by_map(race_key):

    mergable = dict()
    for year in [2024, 2025]:
        for_merge = dislocation[year]
        mergable[year] = for_merge[
            ["ap_black", "abs_racial_dislocation", "racial_dislocation"]
        ].rename(
            columns={
                "racial_dislocation": f"racial_dislocation_{year}",
                "abs_racial_dislocation": f"abs_racial_dislocation_{year}",
            }
        )

    voters_wide = pd.merge(
        mergable[2024],
        mergable[2025],
        left_index=True,
        right_index=True,
        how="outer",
        validate="1:1",
        indicator=True,
    )
    assert (voters_wide._merge == "both").all()
    assert len(mergable[2024]) == len(voters_wide)
    assert (voters_wide["ap_black_x"] == voters_wide["ap_black_y"]).all()

    voters_wide["change_racial_dislocation"] = (
        voters_wide[f"racial_dislocation_{2025}"]
        - voters_wide[f"racial_dislocation_{2024}"]
    )

    avg_change = voters_wide.loc[
        voters_wide["ap_black_x"] == race_key, "change_racial_dislocation"
    ].mean()

    median_change = voters_wide.loc[
        voters_wide["ap_black_x"] == race_key, "change_racial_dislocation"
    ].median()

    fig, ax = plt.subplots()
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
            f"for {racial_groups[race_key]} VAP in Districts 1 and 3",
            y=f"Share of {racial_groups[race_key]} VAP",
            x="Individual-Level Change in Racial Dislocation from 2024 Map to 2025 Map",
        )
        .theme(nick_theme)
        .layout(extent=(0.1, 0.2, 0.9, 0.8))
        .on(ax)
        .plot()
    )
    ax.yaxis.set_ticks([])
    ax.tick_params(axis="x", labelsize=8)
    ax.axvline(x=0, ymin=0, color="grey")
    ax.axvline(
        x=avg_change,
        ymin=0,
        color="red",
        linestyle="dashed",
    )

    ax.axvline(
        x=median_change,
        ymin=0,
        color="blue",
        linestyle="dashed",
    )

    # Add text label alongside the red dashed line
    ax.text(
        avg_change,
        ax.get_ylim()[1] * 0.9,
        f"Average Change: {avg_change:.2f}",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="red",
        fontsize=8,
    )

    ax.text(
        median_change,
        ax.get_ylim()[1] * 0.9,
        f"Median Change: {median_change:.2f}",
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color="blue",
        fontsize=8,
    )

    ax.yaxis.set_ticks([])
    fig.text(
        0.05,
        0.02,
        f"Distribution of individual-level change in Racial Dislocation for {racial_groups[race_key]} VAP in Districts 1 and 3."
        " Negative dislocation values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood (racial dilution)."
        f" Average change indicated with red dashed line, median change indicated with blue dashed line.",
        horizontalalignment="left",
        wrap=True,
        fontsize=7,
    )

    fig.savefig(
        f"../../30_results/distribution_change_race_apblack{race_key}_d1d3.png",
        dpi=600,
        bbox_inches="tight",
    )


for race in racial_groups.keys():
    plot_change_by_map(race)
