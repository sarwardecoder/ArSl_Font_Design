#!/usr/bin/env python3
"""
tools/create_component_layers.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Creates 3 invisible template part-glyphs and links them as reference components
inside handshape slots ASL_001–ASL_005.

Architecture: 60-slot schema (GlyphData.xml)
Toolchain: fontTools (plistlib)
Idempotent: Safe to run multiple times.
"""

import argparse
import sys
import plistlib
import shutil
from pathlib import Path
from datetime import datetime


# ── CONFIG ────────────────────────────────────────────────────────────────────

PART_GLYPHS = [
    "_part.palm",
    "_part.index",
    "_part.thumb",
]

# Target handshape slots that will reference all 3 part glyphs as components
ACTIVE_SLOTS = [f"ASL_{i:03d}" for i in range(1, 6)]  # ASL_001 … ASL_005

# Component offsets per part role (x, y) — relative to each slot's origin
COMPONENT_OFFSETS = {
    "_part.palm":  (0,   0),
    "_part.index": (0,  80),
    "_part.thumb": (60, 40),
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def glyph_filename(name: str) -> str:
    """Convert glyph name to UFO filename: ASL_001 → A_S_L__001.glif"""
    parts = []
    for ch in name:
        if ch.isupper():
            parts.append("_" + ch.lower())
        elif ch == "_":
            parts.append("_")
        else:
            parts.append(ch)
    safe = "".join(parts).lstrip("_")
    return safe + ".glif"


def build_glif_empty(name: str, width: int = 0) -> bytes:
    """Return a minimal GLIF XML for an empty (invisible) glyph."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{name}" format="2">\n'
        f'  <advance width="{width}"/>\n'
        '</glyph>\n'
    )
    return xml.encode("utf-8")


def build_glif_with_components(
    name: str, components: list[dict], width: int = 600
) -> bytes:
    """Return a GLIF XML string embedding named component references."""
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


def load_plist(path: Path) -> dict:
    if path.exists():
        with open(path, "rb") as f:
            return plistlib.load(f)
    return {}


def save_plist(path: Path, data: dict) -> None:
    with open(path, "wb") as f:
        plistlib.dump(data, f, sort_keys=True)


# ── CORE INJECTION ────────────────────────────────────────────────────────────

def inject_component_layers(ufo_path: Path) -> None:
    """
    Inject invisible template parts and link them into ASL_001…ASL_005.
    Idempotent: safe to run multiple times.
    """
    if not ufo_path.exists():
        raise FileNotFoundError(f"UFO not found at '{ufo_path}'.")

    glyphs_dir = ufo_path / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)

    lib_plist = ufo_path / "lib.plist"
    groups_plist = ufo_path / "groups.plist"
    contents_plist = glyphs_dir / "contents.plist"

    # Load existing data
    lib = load_plist(lib_plist)
    groups = load_plist(groups_plist)
    contents = load_plist(contents_plist)

    # Create backup once
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ufo_path.parent / f"{ufo_path.stem}_backup_{ts}.ufo"
    if not backup_path.exists():
        shutil.copytree(ufo_path, backup_path)
        print(f"  [backup] {backup_path}")

    print(f"\n[STEP 1] Injecting invisible template part glyphs …")
    for part_name in PART_GLYPHS:
        filename = glyph_filename(part_name)
        filepath = glyphs_dir / filename
        if not filepath.exists():
            filepath.write_bytes(build_glif_empty(part_name, width=0))
            print(f"  [WRITE] {part_name} → {filename}")
        else:
            print(f"  [SKIP] {part_name} already exists → {filename}")
        contents[part_name] = filename

    print(f"\n[STEP 2] Marking part glyphs as non-exporting …")
    skip_key = "public.skipExportGlyphs"
    existing = lib.get(skip_key, [])
    for name in PART_GLYPHS:
        if name not in existing:
            existing.append(name)
    lib[skip_key] = sorted(existing)
    print(f"  [lib.plist] public.skipExportGlyphs → {sorted(existing)}")

    groups["public.partComponents"] = PART_GLYPHS
    print(f"  [groups.plist] public.partComponents → {PART_GLYPHS}")

    print(f"\n[STEP 3] Linking part components into handshape slots …")
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
        print(f"  [WRITE] {slot_name} → {filename}")
        contents[slot_name] = filename

    # Save all plist changes
    save_plist(lib_plist, lib)
    save_plist(groups_plist, groups)
    save_plist(contents_plist, contents)

    print(f"\n  [SAVE] glyphs/contents.plist updated ({len(contents)} entries).")
    print("=" * 64)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inject component layering system into a UFO source folder."
    )
    parser.add_argument(
        "--ufo",
        default="source/ArSL_Base_Shell.ufo",
        help="Path to the target UFO folder.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ufo_path = Path(args.ufo)

    print("=" * 64)
    print("ArSL Font Project — Component Layer Injector")
    print(f"Target UFO : {ufo_path.resolve()}")
    print("=" * 64)

    try:
        inject_component_layers(ufo_path)
        print(f"\n[SUCCESS] Component layers injected and registered.\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()