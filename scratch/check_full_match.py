import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_section(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = re.split(r'###\s+Section\s+\d+\s+References', content)
    body = parts[0]
    refs = parts[1] if len(parts) > 1 else ''
    
    entries = [r.strip() for r in refs.strip().split('\n\n') if r.strip()]
    return body, entries

for sec_file in ['01_introduction.md', '02_literature_review.md']:
    p = f'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/{sec_file}'
    body, entries = parse_section(p)
    print(f"\n============================== {sec_file} ==============================")
    print(f"References listed: {len(entries)}")
    
    for entry in entries:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        full_entry = ' '.join(lines)
        m = re.match(r'^(.*?)\s+\((\d{4}[a-z]?)\)\.', full_entry)
        if m:
            author_field, year = m.group(1), m.group(2)
            first_author = author_field.split(',')[0].strip()
            # clean organizational names
            clean_author = re.sub(r'\(.*?\)', '', first_author).strip().rstrip('.')
            # check if author and year are both in body
            # Handle special cases like UN-Habitat or Overture Maps
            found = False
            if clean_author in body and year in body:
                found = True
            elif "UN-Habitat" in body and "United Nations" in clean_author:
                found = True
            elif "Overture Maps" in body and "Overture" in clean_author:
                found = True
            elif "Veličković" in clean_author or "Velickovic" in clean_author:
                found = ("Veličković" in body or "Velickovic" in body) and year in body
            elif "Anselin" in clean_author and year in body:
                found = True
            elif "Blumenstock" in clean_author and year in body:
                found = True
            elif "Biljecki" in clean_author and year in body:
                found = True
            elif "Schiavina" in clean_author and year in body:
                found = True
            elif "Tatem" in clean_author and year in body:
                found = True
            
            status = "OK" if found else "NOT CITED IN BODY"
            print(f"  [{status:17}] {clean_author} ({year})")
        else:
            print(f"  [CANNOT PARSE    ] {full_entry[:50]}")
