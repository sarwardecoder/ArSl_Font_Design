#!/usr/bin/env python3
"""
tools/inject_reserved_slots.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Injects placeholder diagonal crosshair glyphs into reserved slots
ASL_046 through ASL_060, completing the 60-slot architecture.
Registers each glyph sequentially into the UFO's contents.plist.
"""

import os
import plistlib
import shutil
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

RESERVED_RANGE = range(46, 61)  # ASL_046 → ASL_060 (inclusive)
GLYPH_PREFIX   = "ASL_"
UFO_PATH       = Path(os.environ.get("ARSL_UFO", "ArSL.ufo"))
GLYPHS_DIR     = UFO_PATH / "glyphs"
CONTENTS_PLIST = GLYPHS_DIR / "contents.plist"

# Diagonal crosshair: two-point line segment (150,150) → (450,450)
GLIF_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<glyph name="{name}" format="2">
  <advance width="600"/>
  <unicode hex="{unicode_hex}"/>
  <outline>
    <contour>
      <point x="150" y="150" type="line"/>
      <point x="450" y="450" type="line"/>
    </contour>
  </outline>
</glyph>
"""

# Private Use Area base: U+F700 offset by slot index (046–060 → U+F72D–U+F73B)
PUA_BASE = 0xF700


# ── Helpers ──────────────────────────────────────────────────────────────────

def glyph_name(index: int) -> str:
    return f"{GLYPH_PREFIX}{index:03d}"


def glif_filename(index: int) -> str:
    return f"ASL_{index:03d}.glif"


def unicode_hex(index: int) -> str:
    return f"{PUA_BASE + index:04X}"


def ensure_glyphs_dir() -> None:
    GLYPHS_DIR.mkdir(parents=True, exist_ok=True)


def load_contents() -> dict:
    if CONTENTS_PLIST.exists():
        with open(CONTENTS_PLIST, "rb") as f:
            return plistlib.load(f)
    return {}


def save_contents(contents: dict) -> None:
    with open(CONTENTS_PLIST, "wb") as f:
        plistlib.dump(contents, f)


def write_glif(index: int) -> Path:
    name     = glyph_name(index)
    filename = glif_filename(index)
    u_hex    = unicode_hex(index)
    dest     = GLYPHS_DIR / filename

    dest.write_text(GLIF_TEMPLATE.format(name=name, unicode_hex=u_hex), encoding="utf-8")
    return dest


# ── Main ─────────────────────────────────────────────────────────────────────

def inject_reserved_slots() -> None:
    ensure_glyphs_dir()
    contents = load_contents()

    injected = []
    skipped  = []

    for idx in RESERVED_RANGE:
        name     = glyph_name(idx)
        filename = glif_filename(idx)

        if name in contents:
            skipped.append(name)
            continue

        write_glif(idx)
        contents[name] = filename
        injected.append((name, filename))

    # Write contents.plist with all entries sorted by glyph name
    sorted_contents = dict(sorted(contents.items()))
    save_contents(sorted_contents)

    # ── Report ───────────────────────────────────────────────────────────────
    print(f"ArSL — Reserved Slot Injection Report")
    print(f"UFO target : {UFO_PATH.resolve()}")
    print(f"Slot range : ASL_046 → ASL_060  ({len(RESERVED_RANGE)} slots)")
    print(f"─" * 52)

    if injected:
        print(f"Injected ({len(injected)}):")
        for name, filename in injected:
            idx = int(name.split("_")[1])
            print(f"  {name}  →  {filename}  [U+{unicode_hex(idx)}]")

    if skipped:
        print(f"Skipped — already present ({len(skipped)}):")
        for name in skipped:
            print(f"  {name}")

    total = len(sorted_contents)
    print(f"─" * 52)
    print(f"contents.plist total entries : {total}")

    if total == 60:
        print(f"✓ 60-slot architecture complete.")
    elif total > 60:
        print(f"⚠ {total} entries present — exceeds 60-slot spec. Review contents.plist.")
    else:
        print(f"✗ Only {total}/60 slots populated — check for missing glyphs.")


if __name__ == "__main__":
    inject_reserved_slots()