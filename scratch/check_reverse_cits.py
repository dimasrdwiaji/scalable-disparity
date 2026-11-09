import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for sec_file in ['01_introduction.md', '02_literature_review.md']:
    p = f'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/{sec_file}'
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = re.split(r'###\s+Section\s+\d+\s+References', content)
    body = parts[0]
    refs = parts[1] if len(parts) > 1 else ''
    
    # Extract years and authors from body
    # Find all 4-digit years in body
    matches = re.findall(r'([A-Z][A-Za-z\u00C0-\u017F\.\s&\-]+?)\s*(?:et\s+al\.)?\s*\(?(\d{4}[a-z]?)\)?', body)
    
    print(f"\n==================== In-text check for {sec_file} ====================")
    # Check against refs
    for m in matches:
        auth_candidate = m[0].strip()
        year = m[1].strip()
        # ignore non-citations (like Section 1, Table 1, 2026, etc)
        if any(w in auth_candidate for w in ['Section', 'Figure', 'Table', 'Resolution', 'Version', 'Equation', 'RQ', 'H3', 'Scale', 'Dimension']):
            continue
        # get last name
        last_word = auth_candidate.split()[-1] if auth_candidate.split() else ''
        if len(last_word) <= 2:
            continue
        # check if in refs
        found_in_refs = (last_word in refs) and (year in refs)
        if not found_in_refs:
            # print for inspection
            print(f"Potential unreferenced in-text citation: '{auth_candidate}' ({year})")
