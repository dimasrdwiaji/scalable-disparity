import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Color Palette Constants
    BG_DARK = RGBColor(15, 23, 42)        # #0F172A Dark Slate/Navy
    BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC Soft Off-White
    PRIMARY_NAVY = RGBColor(15, 30, 54)   # #0F1E36 Deep Navy
    ACCENT_TEAL = RGBColor(0, 168, 150)   # #00A896 Vibrant Teal
    ACCENT_CYAN = RGBColor(14, 134, 212)  # #0E86D4 Bright Blue
    CARD_BG = RGBColor(255, 255, 255)     # #FFFFFF Pure White
    CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0 Subtle Slate Border
    TEXT_MAIN = RGBColor(30, 41, 59)      # #1E293B Deep Charcoal
    TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B Slate Muted
    TEXT_LIGHT = RGBColor(241, 245, 249)  # #F1F5F9 Off-white
    TAG_BG = RGBColor(230, 246, 245)      # Light teal tint
    TAG_TEXT = RGBColor(0, 128, 115)      # Dark teal text
    SUCCESS_BG = RGBColor(240, 253, 244)  # Soft green
    SUCCESS_TEXT = RGBColor(22, 101, 52)  # Deep green
    PENDING_BG = RGBColor(239, 246, 255)  # Soft blue
    PENDING_TEXT = RGBColor(30, 64, 175)  # Deep blue

    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, category_tag, headline, subheader=None):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf = tag_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = category_tag.upper()
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ACCENT_TEAL

        # Headline
        head_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.55))
        tf = head_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = headline
        p.font.name = "Arial"
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_NAVY

        # Subheader if present
        if subheader:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.35))
            tf = sub_box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = subheader
            p.font.name = "Arial"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, fill_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Dark Executive Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s1, BG_DARK)

    # Accent Top Bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(1.8), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_TEAL
    bar.line.fill.background()

    # Pre-title Pill / Tag
    tag_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(10), Inches(0.4))
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    p.text = "GEOAI & EARTH OBSERVATION RESEARCH BRIEFING"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL

    # Main Title
    title_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.5), Inches(1.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Mapping Micro-Scale Physical Living Standards\nand Spatial Segregation via GeoAI"
    p.font.name = "Arial"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(0.8), Inches(3.9), Inches(11.5), Inches(0.8))
    tf = sub_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "An Unsupervised Graph Attention & Multi-Source Remote Sensing Framework"
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Context card at bottom
    c_card = add_card(s1, Inches(0.8), Inches(4.8), Inches(11.733), Inches(1.8), fill_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    c_box = s1.shapes.add_textbox(Inches(1.1), Inches(5.0), Inches(11.1), Inches(1.4))
    tf = c_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "PROGRESS OVERVIEW & EXECUTIVE ARCHITECTURE (5–10 MINUTE BRIEFING)"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL

    p2 = tf.add_paragraph()
    p2.text = "• Scope: Greater Jakarta (Jabodetabek) & Karawang Corridor (~9,800 km² | 17,154 H3 Hexagons | 40.73M Population)"
    p2.font.name = "Arial"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(226, 232, 240)
    p2.space_before = Pt(6)

    p3 = tf.add_paragraph()
    p3.text = "• Purpose: High-level overview of problem definition, spatial lattice design, 10D feature fusion, and GAT-AE segregation detection"
    p3.font.name = "Arial"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: THE CORE MOTIVATION & PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "Problem Statement & Motivation", "Why Remote Sensing of Urban Inequality Demands a Physical Paradigm Shift", "Current socioeconomic indicators fail to capture in-situ physical living conditions in Global South megacities")

    card_w = Inches(3.75)
    card_h = Inches(4.2)
    top_pos = Inches(1.7)

    # Card 1: Urban Dualism
    add_card(s2, Inches(0.8), top_pos, card_w, card_h)
    tb = s2.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Urban Dualism & Micro-Walls"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "Hyper-dense informal settlements (kampungs) and master-planned gated enclaves (kota mandiri) sit directly adjacent to one another."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    p = tf.add_paragraph()
    p.text = "Physical perimeter walls create acute spatial severance and multi-kilometer pedestrian detours within hundreds of meters."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    p = tf.add_paragraph()
    p.text = "Key Takeaway: Disparity in Southeast Asian megacities is micro-spatial, not city-wide concentric rings."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(12)

    # Card 2: MAUP Aggregation Trap
    add_card(s2, Inches(4.78), top_pos, card_w, card_h)
    tb = s2.shapes.add_textbox(Inches(4.98), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. The MAUP Aggregation Trap"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "Official statistics (BPS poverty census, Gini ratios) aggregate at municipal (Kabupaten/Kota) or district levels."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    p = tf.add_paragraph()
    p.text = "Modifiable Areal Unit Problem (MAUP) homogenizes extremes, masking severe deprivation nestled directly inside wealthy administrative units."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    p = tf.add_paragraph()
    p.text = "Key Takeaway: Municipal averages completely blind planners to severe internal spatial segregation."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(12)

    # Card 3: Asset Wealth Trap
    add_card(s2, Inches(8.76), top_pos, card_w, card_h)
    tb = s2.shapes.add_textbox(Inches(8.96), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. The Survey Asset Trap (RWI)"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "Satellite ML wealth models (e.g. Meta RWI) predict household durable goods ownership (smartphones, TVs, motorcycles)."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    p = tf.add_paragraph()
    p.text = "The Paradox: Asset-dense urban households often suffer severe living deficits: <9 m² living space, open drainage, extreme heat, and toxic PM2.5."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    p = tf.add_paragraph()
    p.text = "Key Takeaway: Asset wealth decouples from in-situ physical living conditions in dense urban cores."
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(12)

    # Bottom Core Mission Banner
    add_card(s2, Inches(0.8), Inches(6.1), Inches(11.71), Inches(0.95), fill_color=PRIMARY_NAVY, border_color=None)
    bb = s2.shapes.add_textbox(Inches(1.0), Inches(6.18), Inches(11.3), Inches(0.8))
    tf = bb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "OUR CORE RESEARCH OBJECTIVE:"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL

    p2 = tf.add_paragraph()
    p2.text = "Build an unsupervised, continuous Physical Living Standard Index (PLSI) at sub-kilometer resolution and detect micro-scale spatial segregation boundaries using Graph Neural Networks without ground-truth survey labels."
    p2.font.name = "Arial"
    p2.font.size = Pt(11)
    p2.font.color.rgb = RGBColor(241, 245, 249)
    p2.space_before = Pt(2)

    # =========================================================================
    # SLIDE 3: STUDY AREA & SPATIAL FOUNDATION (H3 LATTICE)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "Study Area & Spatial Architecture", "Uber H3 DGGS Hexagonal Graph Across Greater Jakarta & Karawang", "Establishing an equal-area, MAUP-invariant topological graph lattice for neural message passing")

    # Left Column: Concepts & Stats
    left_w = Inches(5.4)
    top_pos = Inches(1.7)

    # Card: Territory & Demography
    add_card(s3, Inches(0.8), top_pos, left_w, Inches(1.5))
    tb = s3.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.12), left_w - Inches(0.4), Inches(1.25))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Regional Scope & Population Baseline"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• Greater Jakarta (Jabodetabek) + Karawang industrial corridor: ~9,800 km²\n• 15 regencies & municipalities across DKI Jakarta, West Java, and Banten\n• 40,730,836 residents harmonized for 2023 baseline via GHS-POP linear interpolation"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Card: Uber H3 DGGS Lattice
    add_card(s3, Inches(0.8), top_pos + Inches(1.65), left_w, Inches(1.85))
    tb = s3.shapes.add_textbox(Inches(1.0), top_pos + Inches(1.77), left_w - Inches(0.4), Inches(1.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Why Uber H3 Hexagons (Resolution 8)?"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• Equal-Area Geometry: 0.737 km² per cell (edge ~533 m, centroid spacing ~924 m)\n• Isotropic Adjacency: 6 uniform neighbors eliminating square grid diagonal bias\n• Total Graph Size: N = 17,154 nodes and |E| = 101,848 directed spatial edges\n• Eliminates MAUP: Breaks dependency on arbitrary administrative boundaries"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Card: Residential Masking
    add_card(s3, Inches(0.8), top_pos + Inches(3.65), left_w, Inches(1.65))
    tb = s3.shapes.add_textbox(Inches(1.0), top_pos + Inches(3.77), left_w - Inches(0.4), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Residential Filtering & Graph Adjacency"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• Isolated N_res = 9,345 residential cells (Pop ≥ 300, SMOD urban/cluster)\n• Holds 100% of the 40.73M population on 54.5% of territory\n• Crucial GNN Feature: Non-residential cells retained in topological graph to maintain contiguous spatial message passing across water, roads, and parks"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Right Column: Study Area Map Figure
    map_w = Inches(6.1)
    map_h = Inches(5.3)
    add_card(s3, Inches(6.43), top_pos, map_w, map_h)
    img_path = "assets/figures/study_area_map.png"
    if os.path.exists(img_path):
        # Image is 4200x3000 (aspect ratio 1.40)
        # card is 6.1 x 5.3 -> fit image nicely inside with padding
        i_w = Inches(5.8)
        i_h = Inches(4.14)
        s3.shapes.add_picture(img_path, Inches(6.58), top_pos + Inches(0.18), width=i_w)
        # Caption below image
        cb = s3.shapes.add_textbox(Inches(6.58), top_pos + Inches(4.4), i_w, Inches(0.8))
        tf = cb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Figure: Greater Jakarta & Karawang Study Area with 15 Labeled Administrative Jurisdictions, Major Hubs (Soekarno-Hatta, Tanjung Priok, Monas), and Java Inset."
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: MULTI-SOURCE HARMONIZATION & 10D FEATURE SPACE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s4, BG_LIGHT)
    add_header(s4, "Multi-Source Earth Observation Fusion", "17 Datasets Harmonized into 10 Objective Physical Dimensions", "Anchored to Universal Frozen Benchmarks (UN-Habitat, WHO, 15-Minute City) to ensure global transferability")

    # Left Column: The 10 Dimensions Table / List
    left_w = Inches(5.6)
    add_card(s4, Inches(0.8), Inches(1.7), left_w, Inches(5.3))
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.85), left_w - Inches(0.4), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "The 10 Universal Physical Dimensions (2023 Baseline)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    dims = [
        ("X1. Space Sufficiency", "Google Open Buildings 2.5D + GHS-BUILT-C", "Floor area per capita (UN-Habitat 9 m² baseline)"),
        ("X2. Built Density", "Sentinel-2 MSI Level-2A", "Normalized Difference Built-up Index (NDBI)"),
        ("X3. Walkable Amenities", "Overture Maps POIs + OSM Network", "15-min pedestrian Dijkstra network isochrone"),
        ("X4. Bare Soil / Dust", "Sentinel-2 MSI Level-2A", "Bare Soil Index (BSI) capturing unpaved dust"),
        ("X5. Nighttime Energy", "NASA VIIRS Black Marble VNP46A2", "Artificial nocturnal luminosity & electrification"),
        ("X6. Canopy Greenness", "Sentinel-2 MSI Level-2A", "Normalized Difference Vegetation Index (NDVI)"),
        ("X7. Thermal Comfort", "Landsat 8/9 C2 L2 (ST_B10)", "Dry season LST / ΔLST above rural reference"),
        ("X8. Water Access", "Dynamic World 10m + JRC Water", "Surface water recurrence (recreational vs flood)"),
        ("X9. Particulate Purity", "WashU ACAG V6 PM2.5 Surface", "Ground-level fine particulate pollution (WHO)"),
        ("X10. NO2 Purity", "Sentinel-5P TROPOMI NO2", "Tropospheric nitrogen dioxide combustion"),
    ]

    for d_name, d_src, d_desc in dims:
        p = tf.add_paragraph()
        p.text = f"• {d_name}: {d_desc}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(3)

    p_pivots = tf.add_paragraph()
    p_pivots.text = "Key Engineering Pivots:"
    p_pivots.font.name = "Arial"
    p_pivots.font.size = Pt(10)
    p_pivots.font.bold = True
    p_pivots.font.color.rgb = ACCENT_TEAL
    p_pivots.space_before = Pt(8)

    p_piv1 = tf.add_paragraph()
    p_piv1.text = "1. Walkability: Switched from Euclidean buffers to true 15-min street network Dijkstra routing (city2graph) to capture wall barriers.\n2. Thermal Calibration: Screened dry-season Landsat 8/9 scenes and validated against daily MODIS Daytime LST (ρ = 0.882)."
    p_piv1.font.name = "Arial"
    p_piv1.font.size = Pt(8.5)
    p_piv1.font.color.rgb = TEXT_MUTED
    p_piv1.space_before = Pt(2)

    # Right Column: Visual of Feature Maps
    r_w = Inches(5.9)
    add_card(s4, Inches(6.63), Inches(1.7), r_w, Inches(5.3))
    feat_img = "assets/figures/spatial_feature_maps.png"
    if os.path.exists(feat_img):
        # spatial_feature_maps aspect ratio 1.28
        i_w = Inches(5.6)
        s4.shapes.add_picture(feat_img, Inches(6.78), Inches(1.85), width=i_w)
        cb = s4.shapes.add_textbox(Inches(6.78), Inches(6.25), i_w, Inches(0.65))
        tf = cb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Figure: Harmonized Spatial Feature Maps across Greater Jakarta (Built Density, Walkable Amenities, Canopy, LST, PM2.5, and Nighttime Electrification)."
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: GEOAI ARCHITECTURE: SPATIAL GAT-AE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "GeoAI Modeling Methodology", "Spatial Graph Attention Autoencoder (GAT-AE) for Segregation Detection", "Inverting the classic GNN 'over-smoothing' phenomenon to detect micro-scale socio-spatial severance")

    # 3 Pipeline Steps Horizontal Cards
    card_w = Inches(3.75)
    card_h = Inches(3.4)
    top_pos = Inches(1.7)

    # Step 1: Lattice Formulation
    add_card(s5, Inches(0.8), top_pos, card_w, card_h)
    tb = s5.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.18), card_w - Inches(0.4), card_h - Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Step 1: Spatial Graph Formulation"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "• Planar Graph: G = (V, E) defined over 1-ring geometric hex adjacency.\n• Nodes: N = 17,154 total cells (N_modelled = 7,943 cloud-complete residential cells).\n• Edges: |E| = 101,848 directed edges.\n• Node Attributes: X in [0, 1]^(N x 10) standardized against frozen universal physical benchmarks."
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

    # Step 2: Attention Bottleneck
    add_card(s5, Inches(4.78), top_pos, card_w, card_h)
    tb = s5.shapes.add_textbox(Inches(4.98), top_pos + Inches(0.18), card_w - Inches(0.4), card_h - Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Step 2: GAT-AE Latent Bottleneck"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "• 2-Layer GAT Encoder: Computes dynamic edge attention weights alpha_ij reflecting physical feature similarity.\n• Narrow Bottleneck (d = 2): Compresses 10D space into 2D continuous living manifold.\n• Joint Smoothness Loss: Incorporates Graph Laplacian Dirichlet regularization to encourage continuous spatial gradients across normal neighborhoods."
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

    # Step 3: Over-smoothing Inversion
    add_card(s5, Inches(8.76), top_pos, card_w, card_h)
    tb = s5.shapes.add_textbox(Inches(8.96), top_pos + Inches(0.18), card_w - Inches(0.4), card_h - Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Step 3: Disparity Error Spikes"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "• Inverting Over-smoothing: Deep GNNs force neighbors to homogenize. Where an edge crosses a physical wall between luxury and informal housing, conflicting features cannot be reconciled.\n• High Reconstruction Error: Highlights sharp spatial severance seams automatically!\n• Fully Unsupervised: No expensive ground-truth labels required."
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

    # Bottom Full Width Card: Attributed Loss Decomposition
    add_card(s5, Inches(0.8), Inches(5.3), Inches(11.71), Inches(1.7), fill_color=RGBColor(241, 245, 249), border_color=CARD_BORDER)
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(5.42), Inches(11.2), Inches(1.45))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CRUCIAL INNOVATION: ATTRIBUTED ERROR DECOMPOSITION (DOMINANT FRAMEWORK)"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY

    p = tf.add_paragraph()
    p.text = "A simple high reconstruction error could be triggered by natural boundaries (e.g., a river, forest, or park). By decomposing the reconstruction loss along individual channels:\n  Error_built = (Floor Space + Amenities + Built Density) vs. Error_biophysical = (Water + Greenery + LST)\nWe isolate genuine anthropogenic segregation friction surfaces from benign biophysical transitions across the metropolitan fabric."
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 6: PRELIMINARY RESULTS & MICRO-DISPARITY SPOTLIGHT
    # =========================================================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "Case Study Proof-of-Concept", "Resolving Acute Micro-Disparity: BSD City vs. Adjacent Informal Settlement", "Empirical proof of micro-spatial severance across a 200-meter physical boundary in South Tangerang")

    # Top Visual: Case Study Micro-Disparity Triptych
    add_card(s6, Inches(0.8), Inches(1.7), Inches(11.71), Inches(2.9))
    case_img = "assets/figures/case_study_micro_disparity.png"
    if os.path.exists(case_img):
        # case_study_micro_disparity aspect ratio is 3.04 (5332x1756)
        i_w = Inches(11.4)
        s6.shapes.add_picture(case_img, Inches(0.95), Inches(1.8), width=i_w)
        cb = s6.shapes.add_textbox(Inches(0.95), Inches(4.25), i_w, Inches(0.3))
        tf = cb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Visual Triptych: (Left) High-Resolution Satellite View | (Center) 3D Living Floor Area per Capita | (Right) GAT-AE Disparity Edge Boundary"
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_MUTED

    # Bottom 3 Cards: Key Findings
    b_top = Inches(4.75)
    b_h = Inches(2.25)
    b_w = Inches(3.75)

    # Card 1: Floor Space Collapse
    add_card(s6, Inches(0.8), b_top, b_w, b_h)
    tb = s6.shapes.add_textbox(Inches(0.95), b_top + Inches(0.12), b_w - Inches(0.3), b_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Space Deprivation (>5x Collapse)"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• In BSD City: Living floor space exceeds >45 m²/capita with planned multi-story housing.\n• In adjacent Kampung: Drops below <9 m²/capita (UN-Habitat overcrowding threshold).\n• Severance: Occurs across a single concrete perimeter wall within 200 meters."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Card 2: Thermal & Canopy Inequity
    add_card(s6, Inches(4.78), b_top, b_w, b_h)
    tb = s6.shapes.add_textbox(Inches(4.93), b_top + Inches(0.12), b_w - Inches(0.3), b_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Microclimate & Tree Penalty"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• Land Surface Temperature (LST) is up to +4.2 K hotter in dense zinc-roof kampungs.\n• Tree canopy (NDVI) is virtually zero in informal quarters versus lush park corridors in BSD.\n• Demonstrates cumulative environmental injustice at the micro-block scale."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Card 3: 4-Quadrant Divergence
    add_card(s6, Inches(8.76), b_top, b_w, b_h)
    tb = s6.shapes.add_textbox(Inches(8.91), b_top + Inches(0.12), b_w - Inches(0.3), b_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Empirical 4-Quadrant Divergence"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_NAVY
    p = tf.add_paragraph()
    p.text = "• Proves theoretical divergence: Households in the kampung have moderate asset scores (Meta RWI) due to phone/vehicle ownership.\n• However, their in-situ physical environment (PLSI) is severely degraded.\n• GAT-AE edge boundary cleanly flags this interface without labels."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 7: CURRENT STATUS & ROADMAP
    # =========================================================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "Current Progress & Roadmap", "What Is Completed vs. Upcoming Milestones", "Executive status report across the end-to-end research pipeline")

    card_w = Inches(5.7)
    card_h = Inches(4.1)
    top_pos = Inches(1.7)

    # Card 1: Completed Tasks (Green Tint)
    add_card(s7, Inches(0.8), top_pos, card_w, card_h, fill_color=SUCCESS_BG, border_color=RGBColor(187, 247, 208))
    tb = s7.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "COMPLETED MILESTONES (STAGES 1 - 3)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = SUCCESS_TEXT

    completed = [
        "Multi-Source Ingestion Pipeline: Harmonized 17 datasets across EO satellites, building vectors, and street graphs to reference year 2023.",
        "Uber H3 Tessellation: Generated N = 17,154 Res-8 hexagonal lattice with 101,848 planar adjacency edges.",
        "10D Physical Indicators: Formulated & computed all 10 dimensions anchored to Universal Frozen Physical Benchmarks.",
        "Topological Walkability Engine: Integrated city2graph & Overture POIs for true 15-minute pedestrian network isochrones.",
        "Atmospheric Reanalysis: Processed ACAG surface PM2.5 and Sentinel-5P NO2 rasters onto the H3 lattice.",
        "Micro-Disparity Proof-of-Concept: Empirically verified living space and microclimate severance across BSD City vs. Kampung."
    ]
    for item in completed:
        p = tf.add_paragraph()
        p.text = f"✔ {item}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(20, 83, 45)
        p.space_before = Pt(4)

    # Card 2: Upcoming Milestones (Blue Tint)
    add_card(s7, Inches(6.8), top_pos, card_w, card_h, fill_color=PENDING_BG, border_color=RGBColor(191, 219, 254))
    tb = s7.shapes.add_textbox(Inches(7.05), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "UPCOMING MILESTONES (STAGE 4 & BEYOND)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PENDING_TEXT

    upcoming = [
        "Full GAT-AE Autoencoder Training: Scaling unsupervised graph attention training across all 7,943 residential cells.",
        "Latent Manifold Clustering: Evaluating 2D bottleneck representations to identify regional physical living typologies.",
        "Ground-Truth Spatial Validation: Cross-referencing detected segregation friction edges against official municipal slum decrees (RW Kumuh).",
        "Divergence Analysis: Formalizing the 4-quadrant correlation with Meta RWI across all 15 administrative regencies.",
        "Regional Policy Dashboard: Packaging open-access GeoJSON/GeoTIFF raster layers for municipal urban planning."
    ]
    for item in upcoming:
        p = tf.add_paragraph()
        p.text = "➔ " + item
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(30, 58, 138)
        p.space_before = Pt(6)

    # Bottom Discussion Prompt Card
    add_card(s7, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0), fill_color=PRIMARY_NAVY, border_color=None)
    tb = s7.shapes.add_textbox(Inches(1.05), Inches(6.1), Inches(11.2), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "POINTS FOR COLLEAGUE DISCUSSION & INPUT:"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p = tf.add_paragraph()
    p.text = "1. Graph Edge Weights: Recommendations on incorporating physical barriers (railways, toll roads) directly into edge weights.\n2. Potential Additional Sensors: Recommendations on SAR / Sentinel-1 roughness or surface moisture integration."
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(241, 245, 249)
    p.space_before = Pt(2)

    # Save Presentation
    output_path = "docs/presentations/phys_living_index_progress_overview.pptx"
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
