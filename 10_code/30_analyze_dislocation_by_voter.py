import pandas as pd
import numpy as np
import geopandas as gpd

pd.set_option("mode.copy_on_write", True)

#########
# Load
#########

SAMPLE_PCT = 0.01
PROJ = 32119

dislocation = dict()
dists = dict()

for year in [2022, 2024]:
    dislocation[year] = gpd.read_file(
        f"../20_intermediate_data/nc_dislocation_{SAMPLE_PCT:.2f}_sample_map{year}.geojson"
    ).to_crs(epsg=PROJ)

    dists[year] = (
        gpd.read_file(
            f"../00_source_data/district-shapes_{year}/district-shapes/POLYGON.shp"
        )
        .to_crs(epsg=PROJ)
        .rename(columns={"NAME": "district"})
    )

piedmonts = ((350_000, 600_000), (100_000, 325_000))


##########
# By Voters, absolute
##########

for year in [2022, 2024]:
    df = dislocation[year]
    ax = df.sample(frac=0.3).plot(
        "abs_racial_dislocation",
        cmap="Reds",
        legend=True,
        figsize=(9, 4),
        vmin=0,
        vmax=0.35,
        markersize=1,
        alpha=0.5,
    )
    ax.set_title(f"{year} Map")

    dist_scores = df.groupby("district", as_index=False)[
        ["abs_racial_dislocation", "knn_shr_ap_black", "ap_black"]
    ].mean()

    dist = pd.merge(
        dists[year],
        dist_scores,
        on="district",
        how="outer",
        validate="1:1",
        indicator=True,
    )
    dist._merge.value_counts()
    assert dist._merge.value_counts().loc["both"] == 14

    dist.boundary.plot(ax=ax, edgecolor="black", linewidth=0.2)

    dist.apply(
        lambda x: ax.annotate(
            text=f'Dist {x["district"]}, \n{x["ap_black"]:.0%} AP Black',
            xy=x.geometry.centroid.coords[0],
            ha="center",
            fontsize=7,
        ),
        axis=1,
    )
    ax.set_axis_off()
    ax.figure.savefig(f"../30_results/{year}_points.png")

    ax.set_xlim(piedmonts[0])
    ax.set_ylim(piedmonts[1])
    ax.figure.savefig(f"../30_results/{year}_points_piedmonts.png")

#########
# Signed
#########

# Get extreme values
pd_max = 0
pd_min = 0
for year in [2022, 2024]:
    if candidate_max := df.racial_dislocation.max():
        pd_max = candidate_max
    if candidate_min := df.racial_dislocation.min():
        pd_min = candidate_min

limit = max([np.abs(pd_max), np.abs(pd_min)])

# Plot
for year in [2022, 2024]:
    df = dislocation[year]
    ax = df.sample(frac=0.5).plot(
        "racial_dislocation",
        cmap="RdBu",
        legend=True,
        figsize=(9, 4),
        vmin=-limit,
        vmax=limit,
        markersize=1,
        alpha=0.5,
    )
    ax.set_title(f"{year} Map")

    dist_scores = df.groupby("district", as_index=False)[
        ["abs_racial_dislocation", "knn_shr_ap_black", "ap_black"]
    ].mean()

    dist = pd.merge(
        dists[year],
        dist_scores,
        on="district",
        how="outer",
        validate="1:1",
        indicator=True,
    )
    dist._merge.value_counts()
    assert dist._merge.value_counts().loc["both"] == 14

    dist.boundary.plot(ax=ax, edgecolor="black", linewidth=0.2)

    dist.apply(
        lambda x: ax.annotate(
            text=f'Dist {x["district"]}, \n{x["ap_black"]:.0%} AP Black',
            xy=x.geometry.centroid.coords[0],
            ha="center",
            fontsize=7,
        ),
        axis=1,
    )
    ax.legend(title="kNN Share AP Black - Dist Share AP Black")
    ax.set_axis_off()
    ax.figure.savefig(f"../30_results/{year}_signed_dislocation.png")

    ax.set_xlim(piedmonts[0])
    ax.set_ylim(piedmonts[1])
    ax.figure.savefig(f"../30_results/{year}_signed_piedmonts.png")
