import os
import re
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

sys.stdout.reconfigure(encoding='utf-8')

# Read Section 1 and Section 2
path_s1 = 'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/01_introduction.md'
path_s2 = 'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/02_literature_review.md'

with open(path_s1, 'r', encoding='utf-8') as f:
    text_s1 = f.read()

with open(path_s2, 'r', encoding='utf-8') as f:
    text_s2 = f.read()

# Extract references from both
def get_body_and_refs(text):
    parts = re.split(r'###\s+Section\s+\d+\s+References', text)
    body = parts[0]
    refs = parts[1] if len(parts) > 1 else ''
    entries = [r.strip() for r in refs.strip().split('\n\n') if r.strip()]
    return body, entries

body_s1, refs_s1 = get_body_and_refs(text_s1)
body_s2, refs_s2 = get_body_and_refs(text_s2)

# Deduplicate references by first line/DOI
all_refs = {}
for r in refs_s1 + refs_s2:
    lines = [l.strip() for l in r.split('\n') if l.strip()]
    full_r = ' '.join(lines)
    # Use first 35 chars as key
    key = full_r[:40].lower()
    all_refs[key] = full_r

sorted_ref_keys = sorted(all_refs.keys())
consolidated_refs = [all_refs[k] for k in sorted_ref_keys]

print(f"Total consolidated references: {len(consolidated_refs)}")

# Create Word Document
doc = Document()

# Set standard 1-inch margins
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Configure Normal style
style_normal = doc.styles['Normal']
style_normal.font.name = 'Calibri'
style_normal.font.size = Pt(11)
style_normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
style_normal.paragraph_format.line_spacing = 1.15
style_normal.paragraph_format.space_after = Pt(6)

# Title
title_p = doc.add_paragraph()
title_run = title_p.add_run("Scalable GeoAI for Measuring Micro-Scale Physical Living Standards and Spatial Disparities: Integrating Open Buildings, Standardized Point-of-Interest Data, and Graph Attention Autoencoders")
title_run.font.name = 'Calibri'
title_run.font.size = Pt(18)
title_run.font.bold = True
title_run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
title_p.paragraph_format.space_after = Pt(12)
title_p.paragraph_format.space_before = Pt(0)

# Metadata Block
meta_p = doc.add_paragraph()
meta_p.paragraph_format.space_after = Pt(18)
r_author = meta_p.add_run("Author: ")
r_author.bold = True
meta_p.add_run("Dimas RD\n")
r_affil = meta_p.add_run("Affiliation: ")
r_affil.bold = True
meta_p.add_run("Urban Informatics and Spatial Artificial Intelligence Laboratory\n")
r_venue = meta_p.add_run("Target Venue: ")
r_venue.bold = True
meta_p.add_run("ISPRS International Journal of Geo-Information (IJGI) / PLOS ONE / EarthArXiv\n")
r_std = meta_p.add_run("Standard: ")
r_std.bold = True
meta_p.add_run("Publication Manual of the American Psychological Association (7th ed.; APA 7)")

# Abstract Callout Box (Table with left border)
abstract_text = (
    "Measuring socio-spatial disparities and physical living conditions in rapidly urbanizing regions "
    "of the Global South is constrained by spatial data scarcity, administrative boundary aggregation, "
    "and the relative normalization of survey-based wealth models. This study presents an unsupervised "
    "GeoAI framework that maps physical living standards and identifies micro-scale spatial discontinuities "
    "across the 12,800 km² Jabodetabek metropolitan region and Karawang Regency, Indonesia. We combine "
    "Google Open Buildings v3 (2.5D building heights) intersected with European Commission JRC GHS-BUILT-C "
    "residential masks, Overture Maps Foundation points of interest (POIs), Sentinel-2 multi-spectral indices, "
    "Landsat land surface temperature, Open-Meteo air quality reanalysis, and NASA VIIRS nighttime radiance "
    "onto 17,300 Uber H3 Resolution 8 hexagonal cells (~0.74 km²). We formulate a 10-dimensional Physical "
    "Living Standard Index (PLSI) calibrated against international shelter, environmental health, and pedestrian "
    "accessibility guidelines (UN-Habitat 9.0 m² living area baseline, WHO PM2.5 guidelines, and 15-minute "
    "walking catchments). To detect spatial boundaries without ground-truth training labels, we deploy a "
    "Spatial Graph Attention Autoencoder (GAT-AE) over hexagonal geometric adjacency. Constraining latent "
    "dimensionality (d = 2) encourages local spatial continuity, causing reconstruction error to increase "
    "where abrupt feature differences occur across physical and social boundaries dividing master-planned "
    "residential developments from dense informal settlements. Attributed error decomposition distinguishes "
    "socio-spatial boundaries from natural land-cover transitions. A four-quadrant comparison against Meta's "
    "Relative Wealth Index illustrates that asset-based measures can diverge from in-situ physical living "
    "conditions in dense, asset-holding informal neighborhoods. This framework provides urban and regional "
    "planners with an auditable, continuous instrument to evaluate physical living conditions without survey lag."
)

table = doc.add_table(rows=1, cols=1)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = table.cell(0, 0)
tcPr = cell._tc.get_or_add_tcPr()
# Light gray background and dark blue-grey left border
shd = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w')))
borders = parse_xml(r'''<w:tcBorders {} >
    <w:top w:val="none"/>
    <w:left w:val="single" w:sz="24" w:space="0" w:color="0284C7"/>
    <w:bottom w:val="none"/>
    <w:right w:val="none"/>
</w:tcBorders>'''.format(nsdecls('w')))
tcPr.append(shd)
tcPr.append(borders)

ab_p = cell.paragraphs[0]
ab_p.paragraph_format.space_before = Pt(6)
ab_p.paragraph_format.space_after = Pt(6)
ab_p.paragraph_format.left_indent = Inches(0.15)
ab_p.paragraph_format.right_indent = Inches(0.15)

r_ab_head = ab_p.add_run("Abstract\n")
r_ab_head.bold = True
r_ab_head.font.size = Pt(11)
r_ab_head.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

r_ab_body = ab_p.add_run(abstract_text + "\n\n")
r_ab_body.font.size = Pt(10)
r_ab_body.italic = True

r_kw_head = ab_p.add_run("Keywords: ")
r_kw_head.bold = True
r_kw_head.font.size = Pt(9.5)
r_kw = ab_p.add_run("GeoAI, spatial segregation, informal settlements, Graph Attention Networks, H3 discrete global grid, Overture Maps, urban living standards, Global South, urban planning.")
r_kw.font.size = Pt(9.5)

doc.add_paragraph().paragraph_format.space_after = Pt(12)

# Helper to add markdown-like body
def add_markdown_section(doc, md_text):
    lines = md_text.split('\n')
    i = 0
    in_code = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Code block
        if line.startswith('```'):
            if in_code:
                # flush code block
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.left_indent = Inches(0.2)
                r = p.add_run('\n'.join(code_lines))
                r.font.name = 'Courier New'
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        
        if in_code:
            code_lines.append(line)
            i += 1
            continue
            
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
            
        # Ignore title/abstract metadata if repeated
        if stripped.startswith('# Scalable GeoAI') or stripped.startswith('**Author**') or stripped.startswith('### Abstract'):
            # skip until # 1. Introduction
            while i < len(lines) and not lines[i].startswith('# 1. Introduction'):
                i += 1
            continue
            
        # Headings
        if stripped.startswith('# '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[2:])
            r.font.name = 'Calibri'
            r.font.size = Pt(15)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        elif stripped.startswith('## '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[3:])
            r.font.name = 'Calibri'
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        elif stripped.startswith('### '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[4:])
            r.font.name = 'Calibri'
            r.font.size = Pt(11.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        elif stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, stripped[2:])
        elif re.match(r'^\d+\.\s+', stripped):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            num_match = re.match(r'^\d+\.\s+(.*)', stripped)
            add_formatted_runs(p, num_match.group(1))
        elif stripped.startswith('$$') and stripped.endswith('$$'):
            # Math display
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(stripped[2:-2].strip())
            r.font.name = 'Cambria Math'
            r.font.size = Pt(10.5)
            r.italic = True
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            add_formatted_runs(p, stripped)
            
        i += 1

def add_formatted_runs(paragraph, text):
    # Parse bold (**text**), italics (*text*), math ($...$)
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|\$.*?\$)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**'):
            r = paragraph.add_run(token[2:-2])
            r.bold = True
        elif token.startswith('*') and token.endswith('*'):
            r = paragraph.add_run(token[1:-1])
            r.italic = True
        elif token.startswith('$') and token.endswith('$'):
            r = paragraph.add_run(token[1:-1])
            r.font.name = 'Cambria Math'
            r.italic = True
        else:
            paragraph.add_run(token)

# Add Section 1 Body
add_markdown_section(doc, body_s1)

# Add Section 2 Body
add_markdown_section(doc, body_s2)

# Consolidated References Section
h_ref = doc.add_paragraph()
h_ref.paragraph_format.space_before = Pt(24)
h_ref.paragraph_format.space_after = Pt(8)
h_ref.paragraph_format.keep_with_next = True
r = h_ref.add_run("References")
r.font.name = 'Calibri'
r.font.size = Pt(15)
r.font.bold = True
r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

for ref in consolidated_refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    # APA 7 hanging indent
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    
    # Split text and DOI URL
    doi_match = re.search(r'(https?://\S+)', ref)
    if doi_match:
        before_doi = ref[:doi_match.start()]
        doi_url = doi_match.group(1)
        add_formatted_runs(p, before_doi)
        r_doi = p.add_run(doi_url)
        r_doi.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        r_doi.underline = True
    else:
        add_formatted_runs(p, ref)

# Save Document to both paths
out_paths = [
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/manuscript_sections_1_and_2.docx',
    'c:/Users/Dimas RD/Documents/projects/wip/manuscript/manuscript_sections_1_and_2.docx'
]

for out_p in out_paths:
    doc.save(out_p)
    print(f"Successfully saved Word document to: {out_p}")
