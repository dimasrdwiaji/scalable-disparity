import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for name in ['01_introduction.md', '02_literature_review.md']:
    path = f'c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/{name}'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"\nAuditing {name}:")
    # Check for banned fluff terms
    fluff_terms = [
        r'\bfundamentally\b',
        r'\binvaluable\b',
        r'\blong presented\b',
        r'\bsevere\b',
        r'\bvirtually impossible\b',
        r'\bunprecedented\b',
        r'\bgame-changing\b',
        r'\brevolutionary\b',
        r'\bkota mandiri\b',
        r'\brusunawa\b',
        r'\btrap\b'
    ]
    for term in fluff_terms:
        matches = list(re.finditer(term, text, re.IGNORECASE))
        if matches:
            for m in matches:
                # show surrounding context
                start = max(0, m.start() - 30)
                end = min(len(text), m.end() + 30)
                print(f"  [FLAGGED TERM: {term}]: ...{text[start:end].replace(chr(10), ' ')}...")
        else:
            print(f"  [CLEAN] {term}")

print("\nFluff audit complete.")
