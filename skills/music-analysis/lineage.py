#!/usr/bin/env python3
"""
Pink Floyd Production Lineage Explorer

Queries the lineage JSON to show how techniques evolved across albums.
Usage:
    python lineage.py                    # Show all techniques
    python lineage.py technique vcs_3    # Show specific technique evolution
    python lineage.py compare dsotm wywh # Compare two albums
    python lineage.py patterns           # Show cross-album patterns
"""

import sys
import json
from pathlib import Path

LINEAGE_PATH = Path(__file__).parent / "pink-floyd-lineage.json"

def load_lineage():
    """Load the lineage JSON data."""
    with open(LINEAGE_PATH) as f:
        return json.load(f)

def list_techniques(data):
    """List all tracked techniques."""
    print("\n🎛️  TRACKED TECHNIQUES\n")
    print("-" * 50)
    
    for key, tech in data.get("techniques", {}).items():
        name = tech.get("name", key)
        first = tech.get("first_used", "Unknown")
        print(f"  {key:<30} | First: {first}")
    
    print("-" * 50)
    print(f"\n  Total: {len(data.get('techniques', {}))} techniques tracked\n")

def show_technique(data, tech_key):
    """Show evolution of a specific technique."""
    techniques = data.get("techniques", {})
    
    # Find matching technique (case-insensitive, partial match)
    matches = [k for k in techniques if tech_key.lower() in k.lower()]
    
    if not matches:
        print(f"❌ No technique matching '{tech_key}' found.")
        print("\nAvailable techniques:")
        for k in techniques:
            print(f"  - {k}")
        return
    
    for match in matches:
        tech = techniques[match]
        print(f"\n🎛️  {tech.get('name', match).upper()}")
        print("=" * 50)
        print(f"First used: {tech.get('first_used', 'Unknown')}\n")
        
        evolution = tech.get("evolution", {})
        for album, details in evolution.items():
            album_display = album.upper()
            tracks = ", ".join(details.get("tracks", [])) or "N/A"
            notes = details.get("notes", "")
            
            print(f"📀 {album_display}")
            print(f"   Tracks: {tracks}")
            print(f"   Notes: {notes}")
            print()
        
        insight = tech.get("insight", "")
        if insight:
            print(f"💡 Insight: {insight}")
        print()

def compare_albums(data, album1, album2):
    """Compare techniques between two albums."""
    # Normalize album names
    album_map = {
        "dsotm": "dsotm",
        "darkside": "dsotm",
        "dark": "dsotm",
        "wywh": "wywh",
        "wish": "wywh",
        "animals": "animals",
        "wall": "wall",
        "more": "more"
    }
    
    a1 = album_map.get(album1.lower(), album1.lower())
    a2 = album_map.get(album2.lower(), album2.lower())
    
    print(f"\n🎸 COMPARISON: {a1.upper()} vs {a2.upper()}")
    print("=" * 60)
    
    both = []
    only_a1 = []
    only_a2 = []
    
    for key, tech in data.get("techniques", {}).items():
        evolution = tech.get("evolution", {})
        in_a1 = a1 in evolution and evolution[a1].get("tracks")
        in_a2 = a2 in evolution and evolution[a2].get("tracks")
        
        name = tech.get("name", key)
        
        if in_a1 and in_a2:
            both.append(name)
        elif in_a1:
            only_a1.append(name)
        elif in_a2:
            only_a2.append(name)
    
    print(f"\n📀 Both albums:")
    for t in both:
        print(f"   ✅ {t}")
    
    print(f"\n📀 Only {a1.upper()}:")
    for t in only_a1:
        print(f"   🔷 {t}")
    
    print(f"\n📀 Only {a2.upper()}:")
    for t in only_a2:
        print(f"   🔶 {t}")
    
    # Show emotional context if available
    context = data.get("emotional_context", {})
    if a1 in context or a2 in context:
        print(f"\n💭 EMOTIONAL CONTEXT")
        print("-" * 40)
        
        for album in [a1, a2]:
            if album in context:
                ctx = context[album]
                print(f"\n{album.upper()}:")
                print(f"   State: {ctx.get('band_state', 'Unknown')}")
                print(f"   Result: {ctx.get('result', 'Unknown')}")
    
    print()

def show_patterns(data):
    """Show cross-album patterns."""
    patterns = data.get("patterns", {})
    
    print("\n🔄 CROSS-ALBUM PATTERNS")
    print("=" * 60)
    
    for key, pattern in patterns.items():
        name = key.replace("_", " ").title()
        print(f"\n📌 {name}")
        print("-" * 40)
        
        examples = pattern.get("examples", [])
        for ex in examples:
            print(f"   • {ex}")
        
        insight = pattern.get("insight", "")
        if insight:
            print(f"\n   💡 {insight}")
    
    print()

def main():
    data = load_lineage()
    
    if len(sys.argv) < 2:
        list_techniques(data)
        return
    
    command = sys.argv[1].lower()
    
    if command == "technique" and len(sys.argv) > 2:
        show_technique(data, sys.argv[2])
    elif command == "compare" and len(sys.argv) > 3:
        compare_albums(data, sys.argv[2], sys.argv[3])
    elif command == "patterns":
        show_patterns(data)
    elif command == "list":
        list_techniques(data)
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
