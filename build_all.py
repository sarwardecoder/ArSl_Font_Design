#!/usr/bin/env python3
"""
build_all.py
ArSL Font Project — Unified Lifecycle Orchestrator (Windows Validation Fix)
"""

import os
import sys
import plistlib
import shutil
import subprocess
from pathlib import Path

# ── GLOBAL FONT IDENTITY MATRIX ──────────────────────────────────────────────
FONT_NAME_POSTSCRIPT = "ArSL_Font"
FONT_NAME_FULL       = "ArSL Font Regular"
FONT_NAME_FAMILY     = "ArSL Font"

UFO_PATH = Path("source/ArSL_Base_Shell.ufo")
BUILD_DIR = Path("build")

PART_GLYPHS = ["_part.palm", "_part.index", "_part.thumb"]
ALPHABET_SLOTS = [f"ASL_{i:03d}" for i in range(1, 29)]
COMPONENT_OFFSETS = {
    "_part.palm":  (0,   0),
    "_part.index": (0,  20),
    "_part.thumb": (20, 20),
}
EXPR_SLOTS = [f"ASL_{i:03d}" for i in range(41, 46)]
RESERVED_SLOTS = [f"ASL_{i:03d}" for i in range(46, 61)]

def run_step_log(name):
    print(f"\n🚀 [ORCHESTRATOR] Launching Subroutine: {name}...")

def run_agent1_and_2_generation():
    run_step_log("Agent 1 & 2 — Compiling Valid 60-Slot Geometry Schema")
    glyphs_dir = UFO_PATH / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)
    
    with open(UFO_PATH / "metainfo.plist", "wb") as f:
        plistlib.dump({"creator": "ArSL_MultiAgent_Engine", "formatVersion": 3}, f)

    # Inject proper font metrics so Windows sees a valid font structure
    fontinfo_data = {
        "familyName": FONT_NAME_FAMILY,
        "styleName": "Regular",
        "postscriptFontName": FONT_NAME_POSTSCRIPT,
        "unitsPerEm": 1000,
        "ascender": 750,
        "descender": -250,
        "xHeight": 500,
        "capHeight": 700,
        "openTypeNameDesigner": "Sarwar Jahan",
        "versionMajor": 1,
        "versionMinor": 0,
    }
    with open(UFO_PATH / "fontinfo.plist", "wb") as f:
        plistlib.dump(fontinfo_data, f)

    contents = {}
    
    # Crucial Fix: Standard Windows fallback glyph (.notdef)
    contents[".notdef"] = "__notdef.glif"
    notdef_xml = '<?xml version="1.0" encoding="UTF-8"?><glyph name=".notdef" format="2"><advance width="500"/><outline><contour><point x="50" y="0" type="line"/><point x="50" y="700" type="line"/><point x="450" y="700" type="line"/><point x="450" y="0" type="line"/></contour></outline></glyph>'
    (glyphs_dir / "__notdef.glif").write_text(notdef_xml)

    # Step A: Injecting Base Parts WITH VALID GEOMETRY (A small box for the palm base)
    for part in PART_GLYPHS:
        fname = part.replace(".", "_")
        if fname.startswith("_"): fname = "RESERVED_" + fname[1:]
        fname = f"{fname}.glif"
        contents[part] = fname
        
        if part == "_part.palm":
            # Give the base palm real closed vector contours so the font file registers weight
            glif_xml = '<?xml version="1.0" encoding="UTF-8"?><glyph name="_part.palm" format="2"><advance width="600"/><outline><contour><point x="100" y="100" type="line"/><point x="100" y="500" type="line"/><point x="500" y="500" type="line"/><point x="500" y="100" type="line"/></contour></outline></glyph>'
        else:
            glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{part}" format="2"><advance width="0"/></glyph>'
        (glyphs_dir / fname).write_text(glif_xml)

    # Step B: Injecting Alphabet Composite Layouts (ASL_001 - ASL_028)
    for slot in ALPHABET_SLOTS:
        contents[slot] = f"{slot}.glif"
        comps = "".join([f'<component base="{p}" xOffset="{COMPONENT_OFFSETS[p][0]}" yOffset="{COMPONENT_OFFSETS[p][1]}"/>' for p in PART_GLYPHS])
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline>{comps}</outline></glyph>'
        (glyphs_dir / f"{slot}.glif").write_text(glif_xml)

    # Step C: Injecting Facial Expressions (ASL_041 - ASL_045)
    for slot in EXPR_SLOTS:
        contents[slot] = f"{slot}.glif"
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline><contour><point x="200" y="550" type="line"/><point x="300" y="700" type="line"/><point x="400" y="550" type="line"/></contour></outline></glyph>'
        (glyphs_dir / f"{slot}.glif").write_text(glif_xml)

    # Step D: Injecting Reserved Slots (ASL_046 - ASL_060)
    for slot in RESERVED_SLOTS:
        contents[slot] = f"{slot}.glif"
        glif_xml = f'<?xml version="1.0" encoding="UTF-8"?><glyph name="{slot}" format="2"><advance width="600"/><outline><contour><point x="200" y="200" type="line"/><point x="200" y="400" type="line"/><point x="400" y="400" type="line"/><point x="400" y="200" type="line"/></contour></outline></glyph>'
        (glyphs_dir / f"{slot}.glif").write_text(glif_xml)

    with open(glyphs_dir / "contents.plist", "wb") as f:
        plistlib.dump(contents, f, sort_keys=True)
    with open(UFO_PATH / "lib.plist", "wb") as f:
        plistlib.dump({"public.glyphOrder": sorted(list(contents.keys()))}, f)
        
    print(f"✅ Rebranded font internals with compliant global metrics.")

def run_agent3_compilation():
    run_step_log("Agent 3 — Compiling Compliant Production Binaries")
    out_ttf = f"build/{FONT_NAME_POSTSCRIPT}.ttf"
    subprocess.run(["fontmake", "-u", str(UFO_PATH), "-o", "ttf", "--keep-overlaps", "--no-autohint", "--output-path", out_ttf], check=True)
    print(f"✅ Compiled distribution asset: {FONT_NAME_POSTSCRIPT}.ttf")

def main():
    if UFO_PATH.exists(): shutil.rmtree(UFO_PATH)
    if BUILD_DIR.exists(): shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    run_agent1_and_2_generation()
    run_agent3_compilation()
    print("\n" + "=" * 64)
    print(f"🎉 SUCCESS: '{FONT_NAME_FULL}' compiled with valid Windows parameters!")
    print("=" * 64)

if __name__ == "__main__":
    main()