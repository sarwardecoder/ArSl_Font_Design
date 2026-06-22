#!/usr/bin/env python3
"""
tools/inject_reserved_slots.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Injects placeholder diagonal crosshair glyphs into reserved slots
ASL_046 through ASL_060, completing the 60-slot architecture.

Idempotent: Safe to run multiple times.
Compliance: Maintains 60-slot ASL_001..ASL_060 + 3 non-export template glyphs.
"""

import argparse
import sys
import plistlib
from pathlib import Path


# ── CONFIG ────────────────────────────────────────────────────────────────────

RESERVED_RANGE = range(46, 61)  # ASL_046 → ASL_060 (inclusive)

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

# Private Use Area base: U+F700 offset by slot index (046–060 → U+F72E–U+F73C)
PUA_BASE = 0xF700


# ── HELPERS ───────────────────────────────────────────────────────────────────

def glyph_name(index: int) -> str:
    return f"ASL_{index:03d}"


def glif_filename(index: int) -> str:
    # Convert to UFO filename: ASL_046 → A_S_L__046.glif
    parts = []
    base_name = f"ASL_{index:03d}"
    for ch in base_name:
        if ch.isupper():
            parts.append("_" + ch.lower())
        elif ch == "_":
            parts.append("_")
        else:
            parts.append(ch)
    safe = "".join(parts).lstrip("_")
    return safe + ".glif"


def unicode_hex(index: int) -> str:
    return f"{PUA_BASE + index:04X}"


def load_plist(path: Path) -> dict:
    if path.exists():
        with open(path, "rb") as f:
            return plistlib.load(f)
    return {}


def save_plist(path: Path, data: dict) -> None:
    with open(path, "wb") as f:
        plistlib.dump(data, f, sort_keys=True)


# ── CORE INJECTION ────────────────────────────────────────────────────────────

def inject_reserved_slots(ufo_path: Path) -> None:
    """
    Inject reserved ASL_046…ASL_060 glyphs into the UFO.
    Idempotent: skips glyphs already present.
    """
    if not ufo_path.exists():
        raise FileNotFoundError(f"UFO not found at '{ufo_path}'.")

    glyphs_dir = ufo_path / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)
    contents_plist = glyphs_dir / "contents.plist"

    contents = load_plist(contents_plist)

    injected = []
    skipped = []

    for idx in RESERVED_RANGE:
        name = glyph_name(idx)
        filename = glif_filename(idx)
        filepath = glyphs_dir / filename

        if name in contents:
            skipped.append(name)
            continue

        # Write GLIF only if it doesn't already exist on disk
        if not filepath.exists():
            u_hex = unicode_hex(idx)
            glif_content = GLIF_TEMPLATE.format(name=name, unicode_hex=u_hex)
            filepath.write_text(glif_content, encoding="utf-8")

        contents[name] = filename
        injected.append((name, filename))

    # Save contents.plist with sorted keys
    save_plist(contents_plist, contents)

    # ── Report ────────────────────────────────────────────────────────────────
    asl_count = len([k for k in contents.keys() if k.startswith("ASL_")])

    print(f"\nArSL — Reserved Slot Injection Report")
    print(f"UFO target : {ufo_path.resolve()}")
    print(f"Slot range : ASL_046 → ASL_060  ({len(RESERVED_RANGE)} slots)")
    print(f"─" * 60)

    if injected:
        print(f"Injected ({len(injected)}):")
        for name, filename in injected:
            idx = int(name.split("_")[1])
            print(f"  {name}  →  {filename}  [U+{unicode_hex(idx)}]")

    if skipped:
        print(f"Skipped — already present ({len(skipped)}):")
        for name in skipped:
            print(f"  {name}")

    print(f"─" * 60)
    print(f"Total ASL slots populated : {asl_count}/60")

    if asl_count == 60:
        print(f"✓ 60-slot architecture complete.")
    else:
        print(f"✗ Only {asl_count}/60 ASL slots populated.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inject reserved ASL_046..ASL_060 slots into a UFO source folder."
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

    print("=" * 60)
    print("ArSL Font Project — Reserved Slot Injector")
    print(f"Target UFO : {ufo_path.resolve()}")
    print("=" * 60)

    try:
        inject_reserved_slots(ufo_path)
        print(f"\n[SUCCESS] Reserved slots injected.\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
