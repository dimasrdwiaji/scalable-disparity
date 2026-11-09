import re
import os

files = [
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/01_introduction.md',
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/02_literature_review.md'
]

for p in files:
    name = os.path.basename(p)
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = re.split(r'###\s+Section\s+\d+\s+References', content)
    body = parts[0]
    refs = parts[1] if len(parts) > 1 else ''
    
    entries = [r.strip() for r in refs.strip().split('\n\n') if r.strip()]
    print(f"\n==================== {name} ====================")
    print(f"Total Reference Entries: {len(entries)}")
    
    for entry in entries:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        full_entry = ' '.join(lines)
        m = re.match(r'^(.*?)\s+\((\d{4}[a-z]?)\)\.', full_entry)
        if m:
            author_field = m.group(1)
            year = m.group(2)
            first_author = author_field.split(',')[0].strip()
            # Check presence in body
            in_body = (first_author in body) and (year in body)
            status = "FOUND" if in_body else "NOT FOUND IN BODY"
            print(f"[{status:18}] {first_author} ({year})")
        else:
            print(f"[CANNOT PARSE     ] {full_entry[:60]}")
