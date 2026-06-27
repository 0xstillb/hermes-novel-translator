#!/usr/bin/env python3
"""Stats: Show translation progress for a novel project."""
import os, json, glob

def main():
    project = os.getcwd()
    glossary_path = os.path.join(project, "glossary.json")
    chapters_path = os.path.join(project, "chapters.json")
    
    # Count raw files
    raw_en = glob.glob(os.path.join(project, "raw", "*.txt"))
    raw_cn = glob.glob(os.path.join(project, "raw-cn", "*.txt"))
    raw_th = glob.glob(os.path.join(project, "raw-th", "*.txt"))
    translated = glob.glob(os.path.join(project, "translated", "*.md"))
    
    print(f"📊 Translation Progress")
    print(f"{'='*40}")
    print(f"  Raw EN:      {len(raw_en)}")
    print(f"  Raw CN:      {len(raw_cn)}")
    print(f"  Raw TH:      {len(raw_th)}")
    print(f"  Translated:  {len(translated)}")
    
    if os.path.exists(glossary_path):
        with open(glossary_path) as f:
            g = json.load(f)
        chars = g.get("characters", {})
        terms = g.get("terms", {})
        print(f"\n  Glossary:")
        print(f"    Characters: {len(chars)}")
        print(f"    Terms:      {len(terms)}")
    
    if os.path.exists(chapters_path):
        with open(chapters_path) as f:
            ch = json.load(f)
        total = ch.get("total", "?")
        done = sum(1 for c in ch.get("chapters", {}).values() if c.get("status") == "done")
        print(f"\n  Chapters: {done}/{total}")

if __name__ == "__main__":
    main()
