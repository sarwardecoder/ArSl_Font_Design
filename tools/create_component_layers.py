#!/usr/bin/env python3
import os
import plistlib
from pathlib import Path

UFO_PATH = Path("source/ArSL_Base_Shell.ufo")
PART_GLYPHS = ["_part.palm", "_part.index", "_part.thumb"]
ACTIVE_SLOTS = [f"ASL_{i:03d}" for i in range(1, 29)]  # Full Core Alphabet (1-28)

COMPONENT_OFFSETS = {
    "_part.palm":  (0,   0),
    "_part.index": (0,  80),
    "_part.thumb": (60, 40),
}

def glyph_filename(name: str) -> str:
    safe_name = name.replace(".", "_")
    if safe_name.startswith("_"):
        safe_name = "RESERVED_" + safe_name[1:]
    return f"{safe_name}.glif"

def main():
    print("[Agent 2] Generating Core Alphabet Layer Architecture...")
    glyphs_dir = UFO_PATH / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure baseline metainfo exists
    with open(UFO_PATH / "metainfo.plist", "wb") as f:
        plistlib.dump({"creator": "ArSL_Engine", "formatVersion": 3}, f)

    contents_path = glyphs_dir / "contents.plist"
    contents = {}
    if contents_path.exists():
        with open(contents_path, "rb") as f:
            contents = plistlib.load(f)

    # Inject invisible base parts
    for part in PART_GLYPHS:
        fname = glyph_filename(part)
        contents[part] = fname
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{part}" format="2"><advance width="0"/></glyph>'
        (glyphs_dir / fname).write_text(glif_xml)

    # Inject composite alphabet glyph slots
    for slot in ACTIVE_SLOTS:
        fname = glyph_filename(slot)
        contents[slot] = fname
        comps = "".join([f'<component base="{p}" xOffset="{COMPONENT_OFFSETS[p][0]}" yOffset="{COMPONENT_OFFSETS[p][1]}"/>' for p in PART_GLYPHS])
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline>{comps}</outline></glyph>'
        (glyphs_dir / fname).write_text(glif_xml)

    with open(contents_path, "wb") as f:
        plistlib.dump(contents, f, sort_keys=True)
    print(f"✅ Successfully mapped {len(ACTIVE_SLOTS)} alphabet composite slots.")

if __name__ == "__main__":
    main()