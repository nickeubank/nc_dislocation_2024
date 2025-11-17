import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import partisan_dislocation as pdn
from matplotlib import style
from matplotlib_inline.backend_inline import set_matplotlib_formats

set_matplotlib_formats("retina")
nick_theme = {**style.library["seaborn-v0_8-whitegrid"]}
nick_theme.update({"font.sans-serif": ["Fira Sans", "Arial", "sans-serif"]})
plt.rcParams.update(nick_theme)

pd.set_option("mode.copy_on_write", True)

#########
# Load
#########

SAMPLE_PCT = 0.02
PROJ = 32119

dislocation = dict()
dists = dict()

for year in [2022, 2024, 2025]:
    dislocation[year] = gpd.read_file(
        f"../../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}_race.geojson"
    ).to_crs(epsg=PROJ)

    dists[year] = gpd.read_file(
        f"../../20_intermediate_data/ncdistricts_{year}.geojson"
    ).to_crs(epsg=PROJ)


##########
# Plot minority only, signed
##########
signed = True
minority_only = True
# Get map names
map_names = list(dislocation.keys())
if dislocation.keys() != dists.keys():
    raise ValueError("`dislocation` and `dists` keys are not the same.")

# Get range of values to use
pd_max = 0
pd_min = 0
for name in map_names:
    df = dislocation[name]
if candidate_max := df["racial_dislocation"].max():
    pd_max = candidate_max
if candidate_min := df["racial_dislocation"].min():
    pd_min = candidate_min

limit = max([np.abs(pd_max), np.abs(pd_min)])

# cmap
cmap = "RdYlGn"

# Axis bounds

# Plot
plots = dict()
for name in map_names:
    voters = dislocation[name]
    district_polygons = dists[name]

    fig, ax = plt.subplots(figsize=(6, 6))

    map_limits = ((600_000, 940_000), (20_000, 325_000))
    if map_limits is not None:
        limits_in_gpd_format = (
            map_limits[0][0],
            map_limits[1][0],
            map_limits[0][1],
            map_limits[1][1],
        )
        voters = gpd.clip(voters, limits_in_gpd_format)
        district_polygons = gpd.clip(district_polygons, limits_in_gpd_format)

    ax.set_xlim(map_limits[0])
    ax.set_ylim(map_limits[1])
    ax.set_axis_off()

    # If minority_only, split data
    if minority_only is not True:
        voters[voters["ap_black"] != minority_only].sample(frac=0.5).plot(
            ax=ax,
            color="grey",
            markersize=1,
            alpha=0.2,
        )

    voters = voters[voters["ap_black"] == minority_only]

    # Base plot
    voters.plot(
        "racial_dislocation",
        ax=ax,
        cmap=cmap,
        legend=True,
        vmin=-limit,
        vmax=limit,
        markersize=2,
        alpha=0.8,
        legend_kwds={
            "shrink": 0.7,
            "pad": 0.07,
            "location": "left",
        },
    )

    # Get district scores, starting fresh with full dataset of voters
    # in case some were clipped out.
    dist_scores = dislocation[name].groupby("district", as_index=False)[[]].mean()

    dist_poly_w_scores = pd.merge(
        district_polygons,
        dist_scores,
        on="district",
        how="left",
        validate="1:1",
        indicator=True,
    )
    if map_limits is None:
        assert (dist_poly_w_scores._merge == "both").all()
    else:
        assert (dist_poly_w_scores._merge != "left_only").all()

    dist_poly_w_scores.boundary.plot(ax=ax, edgecolor="black", linewidth=0.4)

    #######
    # Add district labels
    #######
    dist_poly_w_scores["district"] = dist_poly_w_scores["district"].astype("str")
    hand_adjustments = {
        "1": (0, 0),
        "2": (0, -10_000),
        "3": (0, 0),
        "4": (0, -1_500),
        "7": (-15_000, -25_000),
        # "8": (0, 0),
        "13": (6_000, -20_000),
    }
    if name == 2025:
        hand_adjustments.update({"13": (6_000, -45_000)})

    def add_district_label(x):

        coords = x.geometry.centroid.coords[0]

        if x["district"] in hand_adjustments.keys():
            coords = (
                coords[0] + hand_adjustments[x["district"]][0],
                coords[1] + hand_adjustments[x["district"]][1],
            )

            ax.annotate(
                text=f"Dist {x["district"]}\n{x["pct_ap_black"]:.0%} Black",
                xy=coords,
                ha="center",
                fontsize=8,
                weight="bold",
            )

    dist_poly_w_scores.apply(add_district_label, axis=1)

    # State Outline
    gpd.GeoSeries([dists[name].geometry.union_all()]).boundary.plot(
        ax=ax, edgecolor="black", linewidth=3
    )

    #######
    # Titles and such
    ######
    dislocation_label_text = "Racial Dislocation"
    fig.suptitle(f"{dislocation_label_text}\n{name} District Map", fontsize=14, y=0.90)

    note_text = (
        f"Racial Dislocation is the share of a voter's district that is"
        " Any Part Black minus the share of the voter's k Nearest "
        "Neighbors who are Any Part Black. Colored dots show racial "
        "dislocation for Any Part Black VAP North Carolineans. Non-Black voters not plotted."
    )

    from textwrap import fill

    wrapped_note = fill(note_text, width=110)

    ax.figure.text(0.01, 0.1, wrapped_note, horizontalalignment="left", fontsize=8)

    # text
    SPACES = 50
    ax.figure.text(
        -0.3,
        0.5,
        f'Concentrated{" "* 10}Racial Dislocation{" "* 10}Diluted      \n("Packed"){" "*SPACES}("Cracked") ',
        transform=ax.transAxes,
        rotation=90,
        va="center",
        ha="center",
        fontsize=10,
    )

    # Store up
    plots[name] = ax

    # Adjust layout to add space on the left for colorbar
    plt.tight_layout(rect=[0.05, 0.13, 1, 0.95])

for p in plots.keys():
    plots[p].figure.savefig(
        f"../../30_results/{p}_signed_dislocation_eastern_nc_minorityonly_race.png",
        dpi=600,
    )
