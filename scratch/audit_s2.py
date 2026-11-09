import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/02_literature_review.md', 'r', encoding='utf-8') as f:
    s2 = f.read()

parts = re.split(r'###\s+Section\s+\d+\s+References', s2)
body = parts[0]
refs = parts[1] if len(parts) > 1 else ''

# Extract all parenthetical citations like (Author, Year) or (Author et al., Year)
paren_cits = re.findall(r'\(([A-Z][A-Za-z\s&,\-\.]+?[0-9]{4}[a-z]?(?:;\s*[A-Z][A-Za-z\s&,\-\.]+?[0-9]{4}[a-z]?)*)\)', body)
all_in_text = []
for p in paren_cits:
    sub = p.split(';')
    for s in sub:
        all_in_text.append(s.strip())

# Also narrative citations like Author et al. (Year) or Author and Author (Year)
narrative = re.findall(r'([A-Z][A-Za-z\-]+(?:\s+et\s+al\.)?(?:\s+and\s+[A-Z][A-Za-z\-]+)?)\s+\(([0-9]{4}[a-z]?)\)', body)
for n in narrative:
    all_in_text.append(f"{n[0]} ({n[1]})")

print(f"Total in-text citation instances extracted: {len(all_in_text)}")
for cit in sorted(set(all_in_text))[:30]:
    print("  CIT:", cit)

ref_entries = [r.strip() for r in refs.strip().split('\n\n') if r.strip()]
print(f"\nTotal references in list: {len(ref_entries)}")
