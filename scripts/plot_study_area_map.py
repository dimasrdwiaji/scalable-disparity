"""
Generate publication-grade Study Area Map for Section 3: Study Area and Dataset.

Displays:
1. Macro-regional bounding box across Greater Jakarta (Jabodetabek) and Karawang (~12,800 km²).
2. Clearly delineated and labeled administrative boundaries for all cities and regencies:
   - DKI Jakarta (and its 5 administrative boroughs)
   - Kota Tangerang, Kota Tangerang Selatan, Kabupaten Tangerang (Banten Province)
   - Kota Depok, Kota Bogor, Kabupaten Bogor, Kota Bekasi, Kabupaten Bekasi, Kabupaten Karawang (West Java)
   - Neighboring peripheral borders (Serang, Lebak, Sukabumi, Cianjur, Bandung Barat)
3. Key geographic features (Java Sea, Mount Salak, Mount Gede, Monas CBD, Ports, Airports).
4. Scale bar, north arrow, coordinate graticules, and a regional Java Island inset locator.
"""

import os
from pathlib import Path

import pyproj

# Ensure PROJ uses the python venv bundle rather than external PostGIS proj.db
os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import contextily as ctx
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import shapely.geometry as sg
from shapely.ops import unary_union

repo_root = Path(__file__).resolve().parent.parent
data_dir = repo_root / "data"
assets_fig_dir = repo_root / "assets" / "figures"
manuscript_fig_dir = repo_root / "manuscript" / "figures"
latex_fig_dir = repo_root / "latex" / "figures"
artifact_dir = Path(r"C:\Users\Dimas RD\.gemini\antigravity\brain\ecf500e3-2cd4-4343-a9ab-e2de20a84561")

for d in [assets_fig_dir, manuscript_fig_dir, latex_fig_dir]:
    d.mkdir(parents=True, exist_ok=True)

# Study bounding box
BBOX = [106.35, -6.75, 107.65, -5.95]


def add_clean_basemap(ax, crs, alpha=0.85):
    """Adds unblocked Contextily basemap (Esri WorldStreetMap primary, OSM HOT fallback)."""
    providers = [
        ("Esri.WorldStreetMap", ctx.providers.Esri.WorldStreetMap),
        ("OpenStreetMap.HOT", ctx.providers.OpenStreetMap.HOT),
    ]
    for name, provider in providers:
        try:
            ctx.add_basemap(ax, crs=crs, source=provider, alpha=alpha, zorder=1)
            return
        except Exception as e:
            print(f"Basemap fallback attempt failed for {name}: {e}")
    print("Warning: All basemap providers failed.")


def create_study_area_map():
    print("Loading administrative boundaries GeoJSON...")
    gdf = gpd.read_file(data_dir / "interim" / "admin_boundaries_study_area.geojson")

    # Define color scheme for jurisdictions
    colors = {
        "Jakarta Selatan": "#e41a1c",
        "Jakarta Timur": "#e41a1c",
        "Jakarta Pusat": "#e41a1c",
        "Jakarta Barat": "#e41a1c",
        "Jakarta Utara": "#e41a1c",
        "South Tangerang City": "#377eb8",
        "Tangerang": "#4daf4a",
        "Kabupaten Tangerang": "#984ea3",
        "Kota Depok": "#ff7f00",
        "Kota Bekasi": "#ffff33",
        "Kabupaten Bekasi": "#a65628",
        "Kota Bogor": "#f781bf",
        "Kabupaten Bogor": "#999999",
        "Kabupaten Karawang": "#66c2a5",
        "Lebak": "#d9d9d9",
        "Serang": "#d9d9d9",
        "Cianjur": "#d9d9d9",
        "Kabupaten Sukabumi": "#d9d9d9",
        "Bandung Barat": "#d9d9d9",
    }

    # Plot figure
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)

    # 1. Base study area background
    ax.set_xlim(BBOX[0], BBOX[2])
    ax.set_ylim(BBOX[1], BBOX[3])

    # Plot administrative polygons with soft pastel semi-transparent fills
    for idx, row in gdf.iterrows():
        cname = row["clean_name"]
        color = colors.get(cname, "#cccccc")
        is_peripheral = cname in ["Lebak", "Serang", "Cianjur", "Kabupaten Sukabumi", "Bandung Barat"]
        alpha_fill = 0.12 if is_peripheral else 0.22
        lw = 1.0 if is_peripheral else 1.8
        ec = "#666666" if is_peripheral else "#222222"
        ls = ":" if is_peripheral else "-"

        gpd.GeoSeries([row.geometry], crs=gdf.crs).plot(
            ax=ax,
            facecolor=color,
            edgecolor=ec,
            linewidth=lw,
            linestyle=ls,
            alpha=alpha_fill,
            zorder=3,
        )

    # Highlight DKI Jakarta unified outer perimeter
    jkt_parts = gdf[gdf["clean_name"].str.startswith("Jakarta")].geometry.tolist()
    if jkt_parts:
        jkt_union = unary_union(jkt_parts)
        gpd.GeoSeries([jkt_union], crs=gdf.crs).plot(
            ax=ax,
            facecolor="none",
            edgecolor="#b30000",
            linewidth=2.4,
            linestyle="-",
            zorder=5,
        )

    # Add unblocked basemap
    add_clean_basemap(ax, crs=gdf.crs.to_string(), alpha=0.82)

    # 2. Add prominent administrative boundary labels with white callout bounding boxes
    labels = [
        # Jakarta Core
        ("DKI JAKARTA\n(Special Capital Region)", 106.840, -6.210, 10.5, "#990000", "bold", "normal"),
        # Banten Province
        ("KOTA TANGERANG", 106.635, -6.175, 9.0, "#004d00", "bold", "normal"),
        ("KOTA TANGERANG\nSELATAN", 106.705, -6.310, 8.5, "#003366", "bold", "normal"),
        ("KABUPATEN TANGERANG", 106.495, -6.180, 10.0, "#4a148c", "bold", "normal"),
        # West Java (Bogor, Depok, Bekasi)
        ("KOTA DEPOK", 106.820, -6.395, 9.0, "#b25900", "bold", "normal"),
        ("KOTA BOGOR", 106.795, -6.595, 8.5, "#880e4f", "bold", "normal"),
        ("KABUPATEN BOGOR\n(Southern Uplands)", 106.850, -6.530, 10.0, "#37474f", "bold", "normal"),
        ("KOTA BEKASI", 106.985, -6.275, 9.0, "#7f6000", "bold", "normal"),
        ("KABUPATEN BEKASI\n(Industrial Core)", 107.125, -6.220, 10.0, "#4e342e", "bold", "normal"),
        ("KABUPATEN KARAWANG\n(Agrarian & Industrial Corridor)", 107.360, -6.250, 10.5, "#004d40", "bold", "normal"),
        # Peripheral Regencies
        ("Kab. Serang", 106.368, -6.110, 8.0, "#555555", "normal", "italic"),
        ("Kab. Lebak", 106.375, -6.520, 8.0, "#555555", "normal", "italic"),
        ("Kab. Sukabumi", 106.680, -6.740, 8.0, "#555555", "normal", "italic"),
        ("Kab. Cianjur (Puncak)", 107.030, -6.735, 8.0, "#555555", "normal", "italic"),
        ("Kab. Bandung Barat", 107.450, -6.735, 8.0, "#555555", "normal", "italic"),
    ]

    for text, x, y, size, color, weight, style in labels:
        ax.text(
            x, y, text,
            fontsize=size,
            fontweight=weight,
            fontstyle=style,
            color=color,
            ha="center",
            va="center",
            zorder=12,
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor="white",
                edgecolor=color,
                alpha=0.88,
                linewidth=0.8,
            ),
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )

    # 3. Add geographic anchors and landmarks
    landmarks = [
        ("Monas CBD", 106.827, -6.175, "*", "#b30000", 120),
        ("Soekarno-Hatta Int'l (CGK)", 106.656, -6.126, "o", "#003366", 60),
        ("Tanjung Priok Port", 106.883, -6.103, "s", "#003366", 60),
        ("BSD City Core", 106.650, -6.307, "s", "#2e7d32", 60),
        ("Cikarang Industrial Hub", 107.150, -6.310, "s", "#e65100", 60),
        ("Mount Salak (2,211m)", 106.730, -6.715, "^", "#1b5e20", 75),
        ("Mount Gede-Pangrango (3,008m)", 106.980, -6.740, "^", "#1b5e20", 75),
    ]

    for name, lon_pt, lat_pt, marker, mcolor, msize in landmarks:
        ax.scatter([lon_pt], [lat_pt], color=mcolor, s=msize, zorder=14, marker=marker, edgecolors="white", linewidths=0.8)
        ax.text(
            lon_pt + 0.018, lat_pt - 0.005, name,
            fontsize=7.8, fontweight="bold", color="#111111", zorder=15,
            bbox=dict(boxstyle="square,pad=0.15", facecolor="#ffffff", alpha=0.85, edgecolor="#888888", linewidth=0.4),
            path_effects=[pe.withStroke(linewidth=1.5, foreground="white")],
        )

    # Water label
    ax.text(
        106.85, -6.00, "JAVA SEA (Teluk Jakarta)",
        fontsize=12, fontweight="bold", fontstyle="italic", color="#1565c0",
        ha="center", va="center", zorder=8, alpha=0.85,
        path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    )

    # 4. Map Scale Bar & North Arrow
    # Approximate at latitude -6.3°: 1 deg lon ~ 110.6 km -> 20 km ~ 0.1808 deg
    scale_x0 = 106.40
    scale_y0 = -6.71
    scale_len_km = 30
    scale_len_deg = scale_len_km / 110.6

    ax.plot([scale_x0, scale_x0 + scale_len_deg], [scale_y0, scale_y0], color="#000000", lw=3.0, zorder=20)
    ax.plot([scale_x0, scale_x0], [scale_y0 - 0.008, scale_y0 + 0.008], color="#000000", lw=2.0, zorder=20)
    ax.plot([scale_x0 + scale_len_deg/2, scale_x0 + scale_len_deg/2], [scale_y0 - 0.005, scale_y0 + 0.005], color="#000000", lw=1.5, zorder=20)
    ax.plot([scale_x0 + scale_len_deg, scale_x0 + scale_len_deg], [scale_y0 - 0.008, scale_y0 + 0.008], color="#000000", lw=2.0, zorder=20)

    ax.text(scale_x0, scale_y0 - 0.018, "0", ha="center", fontsize=8, fontweight="bold", zorder=20)
    ax.text(scale_x0 + scale_len_deg/2, scale_y0 - 0.018, "15", ha="center", fontsize=8, fontweight="bold", zorder=20)
    ax.text(scale_x0 + scale_len_deg, scale_y0 - 0.018, "30 km", ha="center", fontsize=8, fontweight="bold", zorder=20)

    # North arrow
    ax.text(107.59, -6.01, "N\n▲", fontsize=14, fontweight="bold", ha="center", va="center", color="#222222", zorder=20)

    # Study extent bounding box border
    rect = sg.box(BBOX[0], BBOX[1], BBOX[2], BBOX[3])
    gpd.GeoSeries([rect], crs=gdf.crs).plot(
        ax=ax,
        facecolor="none",
        edgecolor="#1a237e",
        linewidth=2.5,
        linestyle="-",
        zorder=10,
    )

    # Set coordinate labels
    ax.set_xlabel("Longitude (°E)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Latitude (°S)", fontsize=10, fontweight="bold")
    ax.set_title(
        "Study Area: Greater Jakarta Metropolitan Agglomeration (Jabodetabek) and Karawang Industrial Corridor\n"
        "Administrative Regencies/Cities across DKI Jakarta, West Java, and Banten Provinces (~12,800 km²)",
        fontsize=12.5,
        fontweight="bold",
        pad=12,
    )

    # 5. Inset Map: Java Island Location
    # Add an inset axes in the top-right corner
    ax_inset = fig.add_axes([0.69, 0.73, 0.20, 0.16])
    ax_inset.set_xlim(105.0, 115.0)
    ax_inset.set_ylim(-9.0, -5.5)
    try:
        ctx.add_basemap(ax_inset, crs="EPSG:4326", source=ctx.providers.Esri.WorldStreetMap, alpha=0.9)
    except Exception:
        pass
    # Highlight study bounding box on inset
    rect_inset = mpatches.Rectangle(
        (BBOX[0], BBOX[1]), BBOX[2] - BBOX[0], BBOX[3] - BBOX[1],
        linewidth=1.8, edgecolor="red", facecolor="red", alpha=0.35, zorder=10
    )
    ax_inset.add_patch(rect_inset)
    ax_inset.text(107.0, -5.7, "Study Area", color="red", fontsize=7.5, fontweight="bold", ha="center")
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    ax_inset.set_title("Location in Java, Indonesia", fontsize=8, fontweight="bold")

    # Legend for Provinces and Jurisdictions
    legend_patches = [
        mpatches.Patch(color="#e41a1c", alpha=0.5, label="DKI Jakarta (Special Capital Region)"),
        mpatches.Patch(color="#377eb8", alpha=0.5, label="Banten (Tangerang, Tangsel, Kab. Tangerang)"),
        mpatches.Patch(color="#4daf4a", alpha=0.5, label="West Java (Bogor, Depok, Bekasi, Karawang)"),
        mpatches.Patch(color="#d9d9d9", alpha=0.5, label="Peripheral Border Regencies"),
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower right",
        fontsize=8.5,
        framealpha=0.92,
        edgecolor="#888888",
        title="Administrative Jurisdiction Tier",
        title_fontsize=9,
    )

    plt.tight_layout()

    # Save figure to assets, manuscript, latex, and artifacts
    p_assets = assets_fig_dir / "study_area_map.png"
    p_manuscript = manuscript_fig_dir / "study_area_map.png"
    p_latex = latex_fig_dir / "study_area_map.png"
    fig.savefig(p_assets)
    fig.savefig(p_manuscript)
    fig.savefig(p_latex)
    if artifact_dir.exists():
        fig.savefig(artifact_dir / "study_area_map.png")

    print(f"Study Area Map successfully generated and saved to {p_assets}, {p_manuscript}, {p_latex}!")
    plt.close(fig)


if __name__ == "__main__":
    create_study_area_map()
