#!/usr/bin/env python3
"""Auto-Glossary: scan raw text files → extract name candidates → propose glossary"""

import re, sys, os, json
from collections import Counter

# Common English words that look like names but aren't
STOPWORDS = {
    'The', 'This', 'That', 'These', 'Those', 'Then', 'Than',
    'When', 'What', 'Where', 'Which', 'Who', 'Whom', 'Whose',
    'With', 'Without', 'Within', 'From', 'There', 'Here',
    'After', 'Before', 'Over', 'Under', 'Very', 'Still',
    'Even', 'Though', 'Also', 'Just', 'Only', 'More',
    'Some', 'Such', 'Both', 'Each', 'Every', 'Many',
    'Into', 'Upon', 'Onto', 'About', 'Down', 'Like',
}

# Known character naming patterns in CN novels (English transliteration)
COMMON_FAMILY_NAMES = {
    'Li', 'Wang', 'Zhang', 'Liu', 'Chen', 'Yang', 'Zhao', 'Huang',
    'Zhou', 'Wu', 'Xu', 'Sun', 'Ma', 'Zhu', 'Hu', 'Lin', 'He',
    'Guo', 'Gao', 'Luo', 'Liang', 'Song', 'Tang', 'Han', 'Deng',
    'Cao', 'Peng', 'Zeng', 'Xiao', 'Tian', 'Dong', 'Pan', 'Yuan',
    'Cai', 'Jiang', 'Yu', 'Du', 'Ye', 'Cheng', 'Su', 'Wei',
    'Lu', 'Shen', 'Ren', 'Yao', 'Lu', 'Zou', 'Xiong', 'Jin',
    'Xue', 'Lei', 'Long', 'Fan', 'Fang', 'Shi', 'Nie', 'Qian',
    'Tang', 'Yan', 'Feng', 'Hao', 'Mo', 'Bai', 'Jun', 'Kong',
}

def scan_names(text):
    """Extract capitalized words that look like names"""
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    return Counter(w for w in words if w not in STOPWORDS and len(w) > 1)

def detect_chinese_name_pattern(name, freq, total_chars):
    """Heuristic: is this likely a character name?"""
    # Family name match
    is_family = name in COMMON_FAMILY_NAMES
    # Appears frequently
    appears_often = freq > max(3, total_chars * 0.001)
    # Single syllable names common in CN novels
    is_short = len(name) <= 4
    
    score = 0
    if is_family: score += 3
    if appears_often: score += 2
    if is_short: score += 1
    
    return score

def load_existing_glossary(path="glossary.json"):
    """Load existing glossary if available"""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"characters": {}, "terms": {}}

def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else ["raw/ch001.txt"]
    
    # Scan all files
    all_names = Counter()
    total_chars = 0
    for f in files:
        if os.path.exists(f):
            text = open(f).read()
            total_chars += len(text)
            all_names += scan_names(text)
            print(f"✅ {f}: {len(scan_names(text))} name candidates")
        else:
            print(f"⚠️  {f}: not found")
    
    if not all_names:
        print("❌ No files found. Usage: python3 auto-glossary.py raw/*.txt")
        sys.exit(1)
    
    # Load existing glossary
    glossary = load_existing_glossary()
    existing = set(glossary.get("characters", {}).keys())
    existing_en = set()
    for ch_name, ch_data in glossary.get("characters", {}).items():
        if "en" in ch_data:
            existing_en.add(ch_data["en"])
    
    print(f"\n{'='*60}")
    print(f"📋 Auto-Glossary Results ({len(files)} files, {total_chars:,} chars)")
    print(f"{'='*60}")
    
    # Known names
    known = [n for n in all_names if n in existing_en or n in existing]
    new_candidates = [(n, f) for n, f in all_names.most_common(50) 
                     if n not in existing_en and n not in existing]
    
    if known:
        print(f"\n✅ Known ({len(known)}):")
        for name in sorted(known)[:15]:
            print(f"    {name:20s} x{all_names[name]:<4d} (in glossary)")
        if len(known) > 15:
            print(f"    ... and {len(known)-15} more")
    
    print(f"\n🔍 New Candidates (top 30 by score):")
    scored = [(n, f, detect_chinese_name_pattern(n, f, total_chars)) 
              for n, f in new_candidates]
    scored.sort(key=lambda x: -x[2])
    
    print(f"\n{'Name':20s} {'Freq':<6s} {'Score':<6s} {'Guess Role'}")
    print(f"{'─'*20} {'─'*6} {'─'*6} {'─'*20}")
    for name, freq, score in scored[:30]:
        role_hint = "protagonist?" if freq > total_chars * 0.01 else \
                    "major?" if score >= 4 else \
                    "side?" if score >= 2 else "minor?"
        print(f"{name:20s} x{freq:<4d} {score:<6d} {role_hint}")
    
    # Suggest glossary additions
    print(f"\n{'='*60}")
    print(f"💡 Suggested additions to glossary.json:")
    print(f"{'='*60}")
    print(f"{{")
    for name, freq, score in scored[:10]:
        print(f'  "{name}": {{')
        print(f'    "en": "{name}",')
        print(f'    "th": "?{name}?",')
        print(f'    "role": "{"protagonist" if score >= 5 else "major" if score >= 3 else "side"}",')
        print(f'    "first_seen": "{files[0].replace("raw/","").replace(".txt","")}"')
        print(f"  }},")
    print(f"}}")
    
    # Stats
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"  Files scanned:     {len(files)}")
    print(f"  Total chars:       {total_chars:,}")
    print(f"  Total candidates:  {len(all_names)}")
    print(f"  Known names:       {len(known)}")
    print(f"  New suggestions:   {len(scored)}")

if __name__ == "__main__":
    main()
