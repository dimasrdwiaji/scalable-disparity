"""
Publication-grade diagnostic visualizations for Stage 3 Feature Engineering.

Generates 4 high-resolution (300 DPI) figures for the manuscript and portfolio:
1. Figure 1: Correlation matrix heatmap across the 10 standardized physical living dimensions.
2. Figure 2: Empirical distributions and boxplots of all 10 feature channels.
3. Figure 3: Regional spatial choropleth panels across Greater Jakarta + Karawang (12,800 km²) with basemap.
4. Figure 4: Micro-scale disparity case study (BSD City master-planned enclave vs. Kampung Sampora).
"""

import os
from pathlib import Path

import pyproj

# Ensure PROJ uses the python venv bundle rather than external PostGIS proj.db
os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Matplotlib configuration for publication-grade formatting
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

repo_root = Path(__file__).resolve().parent.parent
interim_dir = repo_root / "data" / "interim"
processed_dir = repo_root / "data" / "processed"
assets_fig_dir = repo_root / "assets" / "figures"
manuscript_fig_dir = repo_root / "manuscript" / "figures"

assets_fig_dir.mkdir(parents=True, exist_ok=True)
manuscript_fig_dir.mkdir(parents=True, exist_ok=True)

FEATURE_LABELS = {
    "space_sufficiency_ratio": "1. Space Sufficiency (R_space)",
    "residential_plan_area_fraction": "2. Plan Area Fraction (λp_res)",
    "building_compactness": "3. Footprint Compactness (C_bldg)",
    "cumulative_amenities_15m": "4. 15-min Amenities (A_amenity)",
    "vegetation_ndvi": "5. Canopy Cover (NDVI)",
    "heat_island_intensity_inv": "6. Heat Island (dLST_inv)",
    "terrain_safety_inv": "7. Terrain Safety (Slope Safety)",
}

SHORT_LABELS = [
    "R_space",
    "λp_res",
    "C_bldg",
    "A_amenity",
    "NDVI",
    "LST_inv",
    "Safety_inv",
]

LANDMARKS = [
    ("Monas (CBD)", 106.827, -6.175),
    ("Tj. Priok Port", 106.884, -6.103),
    ("Soekarno-Hatta", 106.655, -6.125),
    ("BSD City", 106.650, -6.307),
    ("Bekasi", 106.999, -6.238),
    ("Karawang", 107.305, -6.303),
    ("Bogor", 106.799, -6.597),
]


def add_clean_basemap(ax, crs, alpha=0.88):
    """
    Add a crisp, unblocked basemap using contextily.
    Prefers Esri.WorldStreetMap (clear road labels, topography, zero rate limits / blocks);
    gracefully falls back to OpenStreetMap.HOT.
    """
    providers = [
        ("Esri.WorldStreetMap", ctx.providers.Esri.WorldStreetMap),
        ("OpenStreetMap.HOT", ctx.providers.OpenStreetMap.HOT),
    ]
    for name, provider in providers:
        try:
            ctx.add_basemap(ax, crs=crs, source=provider, alpha=alpha, zorder=1)
            return
        except Exception as e:
            print(f"Basemap fetch attempt failed for {name}: {e}")
    print("Warning: All basemap providers failed to load.")


def save_figure(fig: plt.Figure, base_name: str):
    """Saves figure to assets/figures, manuscript/figures, and artifacts directory."""
    p1 = assets_fig_dir / f"{base_name}.png"
    p2 = manuscript_fig_dir / f"{base_name}.png"
    fig.savefig(p1)
    fig.savefig(p2)
    # Save to conversation artifacts directory if it exists
    artifact_dir = Path(r"C:\Users\Dimas RD\.gemini\antigravity\brain\ecf500e3-2cd4-4343-a9ab-e2de20a84561")
    if artifact_dir.exists():
        fig.savefig(artifact_dir / f"{base_name}.png")
    print(f"Saved {base_name}.png to assets/figures, manuscript/figures, and artifacts.")
    plt.close(fig)


def plot_correlation_matrix(df_proc: pd.DataFrame):
    """Plot Pearson correlation matrix heatmap across 7 normalized dimensions on populated cells."""
    # Filter to populated cells if available
    df_eval = df_proc[df_proc["is_modelled"]] if "is_modelled" in df_proc.columns else df_proc
    cols = list(FEATURE_LABELS.keys())
    corr = df_eval[cols].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(8.5, 7.2))

    cax = ax.imshow(corr.values, cmap="coolwarm", vmin=-1.0, vmax=1.0)
    cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson Correlation Coefficient (r)", rotation=270, labelpad=15)

    ax.set_xticks(range(len(SHORT_LABELS)))
    ax.set_yticks(range(len(SHORT_LABELS)))
    ax.set_xticklabels(SHORT_LABELS, rotation=45, ha="right")
    ax.set_yticklabels(SHORT_LABELS)

    # Annotate values
    for i in range(len(SHORT_LABELS)):
        for j in range(len(SHORT_LABELS)):
            val = corr.iloc[i, j]
            color = "white" if abs(val) > 0.45 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8.5)

    n_eval = len(df_eval)
    ax.set_title(
        f"Figure 1: Cross-Correlation Matrix of 7 Standardized Physical Living Dimensions\n"
        f"(Populated Residential H3 Cells, N = {n_eval:,} Across Greater Jakarta + Karawang)",
        pad=15,
        fontweight="bold",
    )
    save_figure(fig, "feature_correlation_matrix")


def plot_feature_distributions(df_raw: pd.DataFrame, df_proc: pd.DataFrame):
    """Plot empirical histograms / KDE distributions for all 7 standardized features."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 7.5))
    axes = axes.flatten()

    df_eval = df_proc[df_proc["is_modelled"]] if "is_modelled" in df_proc.columns else df_proc
    cols = list(FEATURE_LABELS.keys())

    for idx, col in enumerate(cols):
        ax = axes[idx]
        vals = df_eval[col].to_numpy()

        # Histogram and KDE
        ax.hist(vals, bins=35, density=True, alpha=0.65, color="#1f77b4", edgecolor="white")
        # Median line
        med = float(np.median(vals))
        mean_val = float(np.mean(vals))
        ax.axvline(med, color="#d62728", linestyle="--", linewidth=1.5, label=f"Median ({med:.2f})")
        ax.axvline(mean_val, color="#2ca02c", linestyle=":", linewidth=1.5, label=f"Mean ({mean_val:.2f})")

        ax.set_title(FEATURE_LABELS[col], fontsize=9.5, fontweight="bold")
        ax.set_xlim(-0.02, 1.02)
        ax.set_xlabel("Normalized Value [0.0, 1.0]", fontsize=8.5)
        ax.set_ylabel("Density", fontsize=8.5)
        ax.legend(loc="upper right", fontsize=7.5, frameon=True)
        ax.grid(True, linestyle="--", alpha=0.3)

    # Hide unused 8th subplot
    axes[7].set_visible(False)

    plt.suptitle(
        f"Figure 2: Empirical Distributions of Harmonized Physical Living Standard Indicators\n"
        f"(Populated Residential Cells N = {len(df_eval):,}, Universal Min-Max Scaled into [0.0, 1.0])",
        fontsize=13,
        fontweight="bold",
        y=0.99,
    )
    plt.tight_layout()
    save_figure(fig, "feature_distributions_7d")
    save_figure(fig, "feature_distributions_10d")


def plot_spatial_feature_panels(gdf: gpd.GeoDataFrame):
    """Plot 4-panel regional choropleth maps across Greater Jakarta + Karawang with contextual basemap."""
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    axes = axes.flatten()

    panels = [
        (
            "space_sufficiency_ratio_scaled",
            "YlGnBu",
            "(a) Living Space Sufficiency Ratio (R_space)\nUN-Habitat 9.0 m² Threshold (0.0 to 54.0 m²/capita)",
            "Sufficiency [0, 1]",
        ),
        (
            "cumulative_amenities_15m_scaled",
            "plasma",
            "(b) 15-Minute Pedestrian Amenity Choice (A_amenity)\nBatched Dijkstra Shortest Paths on 174k Overture POIs",
            "Access Index [0, 1]",
        ),
        (
            "vegetation_ndvi_scaled",
            "YlGn",
            "(c) Environmental Vegetative Canopy (NDVI)\nSentinel-2 Terrestrial Urban Canopy Coverage",
            "NDVI Index [0, 1]",
        ),
        (
            "heat_island_intensity_inv_scaled",
            "coolwarm",
            "(d) Thermal Comfort Index (LST Inverted)\nLandsat Microclimatic Surface Cooling (Higher = Cooler)",
            "Comfort Index [0, 1]",
        ),
    ]

    for idx, (col, cmap, title, cbar_label) in enumerate(panels):
        ax = axes[idx]
        # Plot H3 hexes with alpha=0.68 transparency so basemap roads and labels show through
        gdf.plot(
            column=col,
            cmap=cmap,
            linewidth=0.0,
            edgecolor="none",
            legend=True,
            legend_kwds={"label": cbar_label, "orientation": "horizontal", "shrink": 0.65, "pad": 0.05},
            ax=ax,
            vmin=0.0,
            vmax=1.0,
            alpha=0.68,
            zorder=3,
        )
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xlim(106.35, 107.65)
        ax.set_ylim(-6.75, -5.95)
        ax.set_xlabel("Longitude (°E)", fontsize=8.5)
        ax.set_ylabel("Latitude (°S)", fontsize=8.5)

        # Add clean basemap underneath
        add_clean_basemap(ax, crs=gdf.crs.to_string(), alpha=0.88)

        # Add major reference landmarks
        for name, lon_pt, lat_pt in LANDMARKS:
            ax.scatter([lon_pt], [lat_pt], color="#111111", s=25, zorder=10)
            ax.text(
                lon_pt + 0.015, lat_pt, name,
                fontsize=7.5, fontweight="bold", zorder=10,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#666666", linewidth=0.5),
            )

    plt.suptitle(
        "Figure 3: Spatial Distribution of Core Physical Living Standard Dimensions\n"
        "Across Greater Jakarta (Jabodetabek) and Karawang Industrial Corridor (~12,800 km²)\n"
        "(Overlaid on Contextily Basemap with Landmark References)",
        fontsize=13.5,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    save_figure(fig, "spatial_feature_maps")


def plot_micro_scale_case_study(gdf: gpd.GeoDataFrame):
    """
    Plot high-resolution micro-disparity zoom: Master-Planned BSD City vs. Organic Kampung Sampora.
    BSD City / Cisauk / Serpong Bounding Box: [106.60, -6.34, 106.68, -6.27].
    """
    case_bbox = [106.60, -6.34, 106.68, -6.27]
    gdf_sub = gdf.cx[case_bbox[0]:case_bbox[2], case_bbox[1]:case_bbox[3]].copy()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

    # Subplot 1: Living Space Ratio
    gdf_sub.plot(
        column="space_sufficiency_ratio_scaled",
        cmap="Blues",
        linewidth=0.4,
        edgecolor="#333333",
        legend=True,
        ax=axes[0],
        vmin=0.0,
        vmax=1.0,
        alpha=0.72,
        zorder=3,
        legend_kwds={"label": "Normalized R_space", "shrink": 0.7},
    )
    axes[0].set_title(
        "(a) Living Space Sufficiency\n(Sprawling Estates vs. Crowded Kampung)",
        fontsize=10.5,
        fontweight="bold",
    )

    # Subplot 2: Cumulative Amenities
    gdf_sub.plot(
        column="cumulative_amenities_15m_scaled",
        cmap="magma",
        linewidth=0.4,
        edgecolor="#333333",
        legend=True,
        ax=axes[1],
        vmin=0.0,
        vmax=1.0,
        alpha=0.72,
        zorder=3,
        legend_kwds={"label": "Normalized A_amenity", "shrink": 0.7},
    )
    axes[1].set_title(
        "(b) 15-Minute Pedestrian Opportunities\n(Commercial Nodes vs. Peripheral Deserts)",
        fontsize=10.5,
        fontweight="bold",
    )

    # Subplot 3: Canopy Greenness (NDVI)
    gdf_sub.plot(
        column="vegetation_ndvi_scaled",
        cmap="YlGn",
        linewidth=0.4,
        edgecolor="#333333",
        legend=True,
        ax=axes[2],
        vmin=0.0,
        vmax=1.0,
        alpha=0.72,
        zorder=3,
        legend_kwds={"label": "Normalized NDVI", "shrink": 0.7},
    )
    axes[2].set_title(
        "(c) Canopy Vegetation\n(Landscaped Gated Communities vs. Dense Built Roofs)",
        fontsize=10.5,
        fontweight="bold",
    )

    for ax in axes:
        ax.set_xlim(case_bbox[0], case_bbox[2])
        ax.set_ylim(case_bbox[1], case_bbox[3])
        ax.set_xlabel("Longitude (°E)", fontsize=8.5)
        ax.set_ylabel("Latitude (°S)", fontsize=8.5)

        # Add clean basemap
        add_clean_basemap(ax, crs=gdf_sub.crs.to_string(), alpha=0.88)

        # Highlight BSD Green Office Park vs Sampora boundary
        ax.scatter([106.653], [-6.302], color="#d62728", marker="*", s=160, zorder=10, label="Kampung Sampora")
        ax.scatter([106.650], [-6.307], color="#1f77b4", marker="s", s=100, zorder=10, label="BSD Master-Planned")
        ax.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

    plt.suptitle(
        "Figure 4: Micro-Scale Spatial Disparity Case Study: BSD City Master-Planned Enclave vs. Kampung Sampora\n"
        "(Illustrating Abrupt Seams of Spatial Segregation Masked by Municipal BPS Averages)",
        fontsize=12.5,
        fontweight="bold",
        y=0.99,
    )
    plt.tight_layout()
    save_figure(fig, "case_study_micro_disparity")


def main():
    print("Loading interim and processed H3 data...")
    df_raw = pd.read_parquet(interim_dir / "h3_features_raw.parquet")
    fpath = processed_dir / "feature_matrix_7d.parquet"
    if not fpath.exists():
        fpath = processed_dir / "feature_matrix_10d.parquet"
    df_proc = pd.read_parquet(fpath)
    gdf_all = gpd.read_parquet(processed_dir / "h3_hexagons.parquet")

    print(f"Loaded {len(df_raw)} records. Generating publication diagnostic plots...")
    plot_correlation_matrix(df_proc)
    plot_feature_distributions(df_raw, df_proc)
    plot_spatial_feature_panels(gdf_all)
    plot_micro_scale_case_study(gdf_all)
    print("All diagnostic figures successfully rendered and saved!")


if __name__ == "__main__":
    main()
