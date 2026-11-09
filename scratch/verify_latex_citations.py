import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Users/Dimas RD/Documents/projects/phys_living_index/latex/references.bib', 'r', encoding='utf-8') as f:
    bib_text = f.read()

bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_text))
print(f"Total BibTeX keys in references.bib: {len(bib_keys)}")

tex_files = [
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/latex/sections/01_introduction.tex',
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/latex/sections/02_literature_review.tex'
]

cited_keys = set()
for tf in tex_files:
    with open(tf, 'r', encoding='utf-8') as f:
        content = f.read()
    # Find all \cite, \citep, \citet, \citealt, \citeyearpar
    matches = re.findall(r'\\cite[a-z]*\{([^}]+)\}', content)
    for m in matches:
        keys = [k.strip() for k in m.split(',')]
        for k in keys:
            cited_keys.add(k)

print(f"Total cited keys in .tex files: {len(cited_keys)}")

missing = cited_keys - bib_keys
if missing:
    print(f"ERROR: Missing keys in .bib: {missing}")
else:
    print("ALL cited keys exist in references.bib! Perfect match (Zero orphans).")

unused = bib_keys - cited_keys
if unused:
    print(f"Note: Uncited keys in .bib: {unused}")
else:
    print("ALL keys in .bib are cited in the manuscript!")
