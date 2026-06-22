#!/usr/bin/env python3
import plistlib
from pathlib import Path

UFO_PATH = Path("source/ArSL_Base_Shell.ufo")
EXPR_SLOTS = [f"ASL_{i:03d}" for i in range(41, 46)]  # Facial Expressions (41-45)

def main():
    print("[Agent 2] Injecting Facial Expression Non-Manual Markers...")
    glyphs_dir = UFO_PATH / "glyphs"
    contents_path = glyphs_dir / "contents.plist"
    
    with open(contents_path, "rb") as f:
        contents = plistlib.load(f)

    for slot in EXPR_SLOTS:
        fname = f"{slot}.glif"
        contents[slot] = fname
        # Valid closed contour triangle layout placeholder
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline><contour><point x="100" y="400" type="line"/><point x="200" y="600" type="line"/><point x="300" y="400" type="line"/></contour></outline></glyph>'
        (glyphs_dir / fname).write_text(glif_xml)

    with open(contents_path, "wb") as f:
        plistlib.dump(contents, f, sort_keys=True)
    print(f"✅ Successfully injected {len(EXPR_SLOTS)} expression slots.")

if __name__ == "__main__":
    main()