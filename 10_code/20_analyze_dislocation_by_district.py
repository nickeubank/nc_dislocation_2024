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

#########
# District-Level Maps
#########

piedmonts = ((350_000, 600_000), (100_000, 325_000))


for year in [2022, 2024]:
    df = dislocation[year]
    print(
        f"Avg absolute racial dislocation over all voters \n"
        f" for {year} is {df.abs_racial_dislocation.mean():0.4f}"
    )

    dist_scores = df.groupby("district", as_index=False)[
        ["abs_racial_dislocation", "ap_black"]
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
    assert (dist._merge == "both").all()

    print(
        f"Most dislocated district for {year} has "
        f"avg dislocation of {dist.abs_racial_dislocation.max():0.3f}"
    )

    ax = dist.plot(
        "abs_racial_dislocation",
        cmap="Reds",
        legend=True,
        figsize=(9, 4),
        vmin=0,
        vmax=0.225,
    )
    dist.apply(
        lambda x: ax.annotate(
            text=f'Dist {x["district"]}, \n{x["ap_black"]:.0%} AP Black',
            xy=x.geometry.centroid.coords[0],
            ha="center",
            fontsize=7,
        ),
        axis=1,
    )
    dist.boundary.plot(edgecolor="black", ax=ax, linewidth=0.2)
    ax.set_title(f"{year} Map")
    ax.set_axis_off()
    ax.figure.savefig(f"../30_results/{year}_districts.png")

    ax.set_xlim(piedmonts[0])
    ax.set_ylim(piedmonts[1])
    ax.figure.savefig(f"../30_results/{year}_districts_piedmonts.png")
