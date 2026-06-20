#!/usr/bin/env python3
"""
inject_component_layers.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Creates 3 invisible template part-glyphs (_part.palm, _part.index, _part.thumb)
and links them as reference components inside handshape slots ASL_001–ASL_005
inside source/ArSL_Base_Shell.ufo.

Architecture: 60-slot schema (GlyphData.xml)
Toolchain: fontTools (ufoLib2 / plistlib path)
"""

import os
import sys
import plistlib
import shutil
from pathlib import Path
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────

UFO_PATH = Path("source/ArSL_Base_Shell.ufo")

# Template part glyphs — invisible anchors, no advance width needed
PART_GLYPHS = [
    "_part.palm",
    "_part.index",
    "_part.thumb",
]

# Active handshape slots that will reference all 3 part glyphs as components
#ACTIVE_SLOTS = [f"ASL_{i:03d}" for i in range(1, 6)]  # ASL_001 … ASL_005

# Spans systematically across all 28 alphabet slots
ACTIVE_SLOTS = [f"ASL_{i:03d}" for i in range(1, 29)]  # ASL_001 … ASL_028

# Component offsets per part role (x, y) — relative to each slot's origin
COMPONENT_OFFSETS = {
    "_part.palm":  (0,   0),
    "_part.index": (0,  80),
    "_part.thumb": (60, 40),
}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def ufo_glyphs_dir(ufo: Path) -> Path:
    return ufo / "glyphs"

def glyph_filename(name: str) -> str:
    """
    Produce a clean, spec-compliant UFO filename from a glyph name.
    """
    # Standard naming convention to avoid platform namespace collision loops
    safe_name = name.replace(".", "_")
    if safe_name.startswith("_"):
        safe_name = "RESERVED_" + safe_name[1:]
    return f"{safe_name}.glif"

def build_glif_empty(name: str, width: int = 0) -> bytes:
    """Return a minimal GLIF XML for an empty (invisible) glyph."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{name}" format="2">\n'
        f'  <advance width="{width}"/>\n'
        '</glyph>\n'
    )
    return xml.encode("utf-8")

def build_glif_with_components(name: str, components: list[dict], width: int = 600) -> bytes:
    """
    Return a GLIF XML string embedding named component references.
    """
    comp_lines = []
    for c in components:
        comp_lines.append(
            f'    <component base="{c["base"]}" '
            f'xOffset="{c["xOffset"]}" yOffset="{c["yOffset"]}" '
            f'xScale="1" xyScale="0" yxScale="0" yScale="1"/>'
        )
    comp_block = "\n".join(comp_lines)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{name}" format="2">\n'
        f'  <advance width="{width}"/>\n'
        '  <outline>\n'
        f'{comp_block}\n'
        '  </outline>\n'
        '</glyph>\n'
    )
    return xml.encode("utf-8")

# ── CONTENTS.PLIST MANAGEMENT ─────────────────────────────────────────────────

def load_contents(ufo: Path) -> dict:
    contents_path = ufo_glyphs_dir(ufo) / "contents.plist"
    if contents_path.exists():
        with open(contents_path, "rb") as f:
            return plistlib.load(f)
    return {}

def save_contents(ufo: Path, contents: dict) -> None:
    contents_path = ufo_glyphs_dir(ufo) / "contents.plist"
    with open(contents_path, "wb") as f:
        plistlib.dump(contents, f, sort_keys=True)

# ── LIB.PLIST — mark part glyphs as non-exporting ────────────────────────────

def load_lib(ufo: Path) -> dict:
    lib_path = ufo / "lib.plist"
    if lib_path.exists():
        with open(lib_path, "rb") as f:
            return plistlib.load(f)
    return {}

def save_lib(ufo: Path, lib: dict) -> None:
    lib_path = ufo / "lib.plist"
    with open(lib_path, "wb") as f:
        plistlib.dump(lib, f, sort_keys=True)

def mark_parts_non_exporting(ufo: Path, part_names: list[str]) -> None:
    lib = load_lib(ufo)
    skip_key = "public.skipExportGlyphs"
    existing = lib.get(skip_key, [])
    for name in part_names:
        if name not in existing:
            existing.append(name)
    lib[skip_key] = sorted(existing)
    save_lib(ufo, lib)
    print(f"  [lib.plist] public.skipExportGlyphs → {sorted(existing)}")

# ── GROUPS.PLIST — register component group ───────────────────────────────────

def register_part_group(ufo: Path, part_names: list[str]) -> None:
    groups_path = ufo / "groups.plist"
    if groups_path.exists():
        with open(groups_path, "rb") as f:
            groups = plistlib.load(f)
    else:
        groups = {}

    groups["public.partComponents"] = part_names

    with open(groups_path, "wb") as f:
        plistlib.dump(groups, f, sort_keys=True)
    print(f"  [groups.plist] public.partComponents → {part_names}")

# ── BACKUP ────────────────────────────────────────────────────────────────────

def backup_ufo(ufo: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = ufo.parent / f"{ufo.stem}_backup_{ts}.ufo"
    shutil.copytree(ufo, dest)
    print(f"  [backup] {dest}")
    return dest

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 64)
    print("ArSL Font Project — Component Layer Injector")
    print(f"Target UFO : {UFO_PATH.resolve()}")
    print("=" * 64)

    if not UFO_PATH.exists():
        print(f"\n[ERROR] {UFO_PATH} not found. Run baseline setup first.")
        sys.exit(1)

    print(f"\n[INFO] UFO found. Creating workspace backup …")
    backup_ufo(UFO_PATH)

    glyphs_dir = ufo_glyphs_dir(UFO_PATH)
    contents = load_contents(UFO_PATH)

    # Inject template parts
    print("\n[STEP 1] Injecting invisible template part glyphs …")
    for part_name in PART_GLYPHS:
        filename = glyph_filename(part_name)
        filepath = glyphs_dir / filename
        filepath.write_bytes(build_glif_empty(part_name, width=0))
        print(f"  [WRITE] {part_name} → {filename}")
        contents[part_name] = filename

    print("\n[STEP 2] Marking part glyphs as non-exporting …")
    mark_parts_non_exporting(UFO_PATH, PART_GLYPHS)
    register_part_group(UFO_PATH, PART_GLYPHS)

    # Link paths across target slots
    print("\n[STEP 3] Linking part components into active handshape slots …")
    for slot_name in ACTIVE_SLOTS:
        filename = glyph_filename(slot_name)
        filepath = glyphs_dir / filename

        component_defs = [
            {
                "base": part,
                "xOffset": COMPONENT_OFFSETS[part][0],
                "yOffset": COMPONENT_OFFSETS[part][1],
            }
            for part in PART_GLYPHS
        ]

        filepath.write_bytes(
            build_glif_with_components(slot_name, component_defs, width=600)
        )
        print(f"  [WRITE] {slot_name} → {filename} (components: {[c['base'] for c in component_defs]})")
        contents[slot_name] = filename

    save_contents(UFO_PATH, contents)
    print(f"\n  [SAVE] glyphs/contents.plist updated ({len(contents)} entries).")
    print("=" * 64)

if __name__ == "__main__":
    main()