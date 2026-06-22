#!/usr/bin/env python3
import plistlib
from pathlib import Path

UFO_PATH = Path("source/ArSL_Base_Shell.ufo")
RESERVED_SLOTS = [f"ASL_{i:03d}" for i in range(46, 61)]  # Expansion Space (46-60)

def main():
    print("[Agent 2] Initializing Dialect Expansion Space...")
    glyphs_dir = UFO_PATH / "glyphs"
    contents_path = glyphs_dir / "contents.plist"
    
    with open(contents_path, "rb") as f:
        contents = plistlib.load(f)

    for slot in RESERVED_SLOTS:
        fname = f"{slot}.glif"
        contents[slot] = fname
        # Valid closed contour square box layout placeholder
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline><contour><point x="150" y="150" type="line"/><point x="150" y="450" type="line"/><point x="450" y="450" type="line"/><point x="450" y="150" type="line"/></contour></outline></glyph>'
        (glyphs_dir / fname).write_text(glif_xml)

    with open(contents_path, "wb") as f:
        plistlib.dump(contents, f, sort_keys=True)

    # Preserve lib.plist and only update glyphOrder
    lib_path = UFO_PATH / "lib.plist"
    lib = {}
    if lib_path.exists():
        with open(lib_path, "rb") as f:
            lib = plistlib.load(f)
    lib["public.glyphOrder"] = sorted(list(contents.keys()))
    with open(lib_path, "wb") as f:
        plistlib.dump(lib, f)
        
    print(f"✅ Successfully preserved {len(RESERVED_SLOTS)} dialect expansion slots.")

if __name__ == "__main__":
    main()