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

for year in [2022, 2025]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)
    print(year)
    dislocation[year] = dislocation[year][dislocation[year]["ap_black"] == 1]
    dislocation[year].plot(markersize=1, alpha=0.7)

########
# Plot Dislocation Histograms by Map
########


voters = list()
for year in [2022, 2025]:
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

    if year == 2022:
        one_year_voters["Map"] = f"2022 Map"

    if year == 2025:
        one_year_voters["Map"] = f"2025 Map"

    voters.append(one_year_voters)

voter_subset = pd.concat(voters)
assert (voter_subset["ap_black"] == 1).all()
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
        title=f"Statewide Racial Dislocation for Black VAP\nFrom 2022 to 2025",
        y=f"Share of AP Black VAP",
        x=f"(Dilution){" "*20}VAP Racial Dislocation Score{" "*20}(Concentration)",
    )
    .limit(x=(-0.2, 0.2))
    .theme(nick_theme)
    .layout(extent=(0.1, 0.2, 0.90, 0.8))
    .on(ax)
    .plot()
)

ax.axvline(x=0, ymin=0, color="grey")

means = dict()
medians = dict()
for i in [2022, 2025]:
    means[i] = voter_subset.loc[
        (voter_subset["map"] == i),
        "racial_dislocation",
    ].mean()
    medians[i] = voter_subset.loc[
        (voter_subset["map"] == i),
        "racial_dislocation",
    ].median()

ax.axvline(
    x=means[2022],
    ymin=0,
    color="blue",
    linestyle="solid",
)
ax.text(
    means[2022],
    ax.get_ylim()[1] * 0.95,
    "Mean, 2022",
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
    ax.get_ylim()[1] * 0.95,
    "Mean, 2025",
    rotation=90,
    verticalalignment="top",
    horizontalalignment="right",
    color="black",
    fontsize=8,
)

ax.axvline(
    x=medians[2022],
    ymin=0,
    color="blue",
    linestyle="dashed",
)
ax.text(
    medians[2022],
    ax.get_ylim()[1] * 0.1,
    "Median, 2022",
    rotation=90,
    verticalalignment="bottom",
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
    ax.get_ylim()[1] * 0.1,
    "Median, 2025",
    rotation=90,
    verticalalignment="bottom",
    horizontalalignment="right",
    color="black",
    fontsize=8,
)

mean_change = (
    f"Avg Dislocation, 2022: {means[2022]:.3f}\n"
    f"Avg Dislocation, 2025: {means[2025]:.3f}"
)

median_change = (
    f"Median Dislocation, 2022: {medians[2022]:.3f}\n"
    f"Median Dislocation, 2025: {medians[2025]:.3f}"
)

# Add text in top right quadrant
ax.text(
    -0.195,
    3.5,
    mean_change,
    fontsize=8,
    verticalalignment="top",
    horizontalalignment="left",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)

ax.text(
    -0.195,
    3,
    median_change,
    fontsize=8,
    verticalalignment="top",
    horizontalalignment="left",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)

ax.yaxis.set_ticks([])
ax.tick_params(axis="x", labelsize=8)
fig.legends[0].set_bbox_to_anchor((0.9, 0.7))
fig.text(
    0.05,
    0.02,
    f"Distribution of Racial Dislocation across statewide AP Black VAP."
    " Negative values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood."
    " Average values indicated with solid blue and orange lines, median values indicated with dashed lines.",
    horizontalalignment="left",
    wrap=True,
    fontsize=8,
)

fig.savefig(
    f"../../30_results/dislocation_densities_race_apblack_statewide_2022v2025.png",
    dpi=600,
    bbox_inches="tight",
)


#############
# Measure individual-level change
#############


mergable = dict()
for year in [2022, 2025]:
    for_merge = dislocation[year]
    mergable[year] = for_merge[
        ["ap_black", "abs_racial_dislocation", "racial_dislocation", "geometry"]
    ].rename(
        columns={
            "racial_dislocation": f"racial_dislocation_{year}",
            "abs_racial_dislocation": f"abs_racial_dislocation_{year}",
        }
    )

voters_wide = pd.merge(
    mergable[2022],
    mergable[2025],
    left_index=True,
    right_index=True,
    how="outer",
    validate="1:1",
    indicator=True,
)

assert (voters_wide["ap_black_x"] == 1).all()
assert (voters_wide["ap_black_y"] == 1).all()
assert (voters_wide._merge == "both").all()
assert len(mergable[2022]) == len(voters_wide)

voters_wide["change_racial_dislocation"] = (
    voters_wide[f"racial_dislocation_{2025}"]
    - voters_wide[f"racial_dislocation_{2022}"]
)

avg_change = voters_wide.loc[
    voters_wide["ap_black_x"] == 1, "change_racial_dislocation"
].mean()

median_change = voters_wide.loc[
    voters_wide["ap_black_x"] == 1, "change_racial_dislocation"
].median()

fig, ax = plt.subplots()
(
    so.Plot(
        voters_wide.loc[voters_wide["ap_black_x"] == 1, ["change_racial_dislocation"]],
        x="change_racial_dislocation",
    )
    .add(so.Area(), so.KDE(bw_adjust=2))
    .label(
        title=f"Statewide Individual-Level Change\nin Racial Dislocation "
        "for Black VAP\nFrom 2022 To 2025",
        y=f"Share of Black VAP",
        x="Individual-Level Change in Racial Dislocation from 2022 Plan to 2025 Plan",
    )
    .theme(nick_theme)
    .limit(x=(-0.25, 0.22))
    .layout(extent=(0.1, 0.2, 0.9, 0.8))
    .on(ax)
    .plot()
)
ax.yaxis.set_ticks([])
ax.tick_params(axis="x", labelsize=8)
ax.axvline(x=0, ymin=0, color="grey", alpha=0.5)
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
    ax.get_ylim()[1] * 0.6,
    f"Average Change: {avg_change:.2f}",
    rotation=90,
    verticalalignment="top",
    horizontalalignment="right",
    color="red",
    fontsize=8,
)

ax.text(
    median_change,
    ax.get_ylim()[1] * 0.6,
    f"Median Change: {median_change:.2f}",
    rotation=270,
    verticalalignment="top",
    horizontalalignment="left",
    color="blue",
    fontsize=8,
)

ax.yaxis.set_ticks([])
fig.text(
    0.05,
    0.02,
    f"Distribution of individual-level change in Racial Dislocation for statewide AP Black VAP."
    " Negative dislocation values indicate a person's district has a lower Any Part Black composition than their geographic neighborhood (racial dilution)."
    f" Average change indicated with red dashed line, median change indicated with blue dashed line.",
    horizontalalignment="left",
    wrap=True,
    fontsize=7,
)

fig.savefig(
    f"../../30_results/distribution_change_race_apblack_statewide_2022v2025.png",
    dpi=600,
    bbox_inches="tight",
)
