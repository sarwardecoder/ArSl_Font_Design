"""
tools/inject_expression_markers.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Injects closed triangular placeholder contours into facial expression /
non-manual marker slots ASL_041–ASL_045 inside:
    source/ArSL_Base_Shell.ufo

Operations performed:
  1. Write one GLIF file per slot into ufo/glyphs/
  2. Patch ufo/glyphs/contents.plist (adds only the 5 new entries)
  3. Patch ufo/lib.plist  (publicGlyphOrder — appends after ASL_040)
  4. Leaves ALL existing slots (ASL_001–ASL_040) strictly untouched.
"""

import os
import plistlib
import textwrap

# ── Config ────────────────────────────────────────────────────────────────────
UFO_PATH        = os.path.join("source", "ArSL_Base_Shell.ufo")
GLYPHS_DIR      = os.path.join(UFO_PATH, "glyphs")
CONTENTS_PLIST  = os.path.join(GLYPHS_DIR, "contents.plist")
LIB_PLIST       = os.path.join(UFO_PATH, "lib.plist")

# PUA block E041–E045 (immediately follows movement marker range)
EXPRESSION_SLOTS = [
    ("ASL_041", 0xE041),
    ("ASL_042", 0xE042),
    ("ASL_043", 0xE043),
    ("ASL_044", 0xE044),
    ("ASL_045", 0xE045),
]

# Closed triangular placeholder — identical anchor triangle, unique per slot
# via a per-slot vertical offset (DELTA_Y) so every GLIF is byte-distinct.
DELTA_Y = 20   # y offset increment per slot

GLIF_TEMPLATE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <glyph name="{glyph_name}" format="2">
      <advance width="400"/>
      <unicode hex="{unicode_hex}"/>
      <outline>
        <contour>
          <point x="100" y="{y_base}"  type="line" name="p1"/>
          <point x="200" y="{y_tip}"   type="line" name="p2"/>
          <point x="300" y="{y_base}"  type="line" name="p3"/>
        </contour>
      </outline>
    </glyph>
""")


# ── Helpers ───────────────────────────────────────────────────────────────────

def glyph_name_to_filename(name: str) -> str:
    """
    UFO filename convention: replace uppercase letters with underscore+lower,
    then append '.glif'.  ASL_041 → A_S_L__041.glif
    Follows the AGLFN-safe scheme used by RoboFont / fontmake.
    """
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


def load_plist(path: str) -> object:
    with open(path, "rb") as fh:
        return plistlib.load(fh)


def save_plist(path: str, data: object) -> None:
    with open(path, "wb") as fh:
        plistlib.dump(data, fh, sort_keys=False)
    print(f"  [plist] saved → {path}")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# ── Core injection ────────────────────────────────────────────────────────────

def write_glif_files() -> dict:
    """
    Write one GLIF per expression slot.
    Returns {glyph_name: filename} for contents.plist patching.
    """
    ensure_dir(GLYPHS_DIR)
    new_entries: dict = {}

    for idx, (glyph_name, codepoint) in enumerate(EXPRESSION_SLOTS):
        filename    = glyph_name_to_filename(glyph_name)
        glif_path   = os.path.join(GLYPHS_DIR, filename)
        unicode_hex = f"{codepoint:04X}"
        y_base      = 400 + idx * DELTA_Y
        y_tip       = 600 + idx * DELTA_Y

        glif_content = GLIF_TEMPLATE.format(
            glyph_name  = glyph_name,
            unicode_hex = unicode_hex,
            y_base      = y_base,
            y_tip       = y_tip,
        )

        with open(glif_path, "w", encoding="utf-8") as fh:
            fh.write(glif_content)

        new_entries[glyph_name] = filename
        print(f"  [glif] {glyph_name}  U+{unicode_hex}  → glyphs/{filename}")

    return new_entries


def patch_contents_plist(new_entries: dict) -> None:
    """
    Merge new_entries into contents.plist.
    Skips any key already present (idempotent re-runs safe).
    Never removes or reorders existing keys.
    """
    if os.path.exists(CONTENTS_PLIST):
        contents: dict = load_plist(CONTENTS_PLIST)
    else:
        contents = {}

    added = 0
    for glyph_name, filename in new_entries.items():
        if glyph_name not in contents:
            contents[glyph_name] = filename
            added += 1
        else:
            print(f"  [contents.plist] skipped (already present): {glyph_name}")

    save_plist(CONTENTS_PLIST, contents)
    print(f"  [contents.plist] +{added} new entries added.")


def patch_lib_plist(new_entries: dict) -> None:
    """
    Append new glyph names to public.glyphOrder in lib.plist,
    inserted immediately after ASL_040 when found, otherwise appended.
    Skips names already present (idempotent).
    """
    if not os.path.exists(LIB_PLIST):
        print(f"  [lib.plist] not found at {LIB_PLIST} — skipping glyph order patch.")
        return

    lib: dict        = load_plist(LIB_PLIST)
    order: list      = lib.get("public.glyphOrder", [])
    new_names        = [n for n in new_entries if n not in order]

    if not new_names:
        print("  [lib.plist] all expression slots already in public.glyphOrder.")
        return

    anchor = "ASL_040"
    if anchor in order:
        insert_pos = order.index(anchor) + 1
        order[insert_pos:insert_pos] = new_names
        print(f"  [lib.plist] inserted after {anchor}: {new_names}")
    else:
        order.extend(new_names)
        print(f"  [lib.plist] appended (ASL_040 anchor not found): {new_names}")

    lib["public.glyphOrder"] = order
    save_plist(LIB_PLIST, lib)


# ── Guard: confirm we are not touching protected slots ────────────────────────

def verify_no_protected_slots_touched(new_entries: dict) -> None:
    protected_prefixes = [f"ASL_{str(i).zfill(3)}" for i in range(1, 41)]
    for name in new_entries:
        assert name not in protected_prefixes, (
            f"ABORT: {name} collides with a protected handshape/movement slot."
        )
    print("  [guard] protected slot check passed — ASL_001–ASL_040 untouched.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n[ArSL] inject_expression_markers.py")
    print(f"[ArSL] Target UFO : {os.path.abspath(UFO_PATH)}")
    print(f"[ArSL] Slots      : ASL_041 → ASL_045  (facial / non-manual markers)\n")

    if not os.path.isdir(UFO_PATH):
        raise FileNotFoundError(
            f"UFO not found at '{UFO_PATH}'. "
            "Run from the repository root or adjust UFO_PATH."
        )

    new_entries = write_glif_files()
    verify_no_protected_slots_touched(new_entries)
    patch_contents_plist(new_entries)
    patch_lib_plist(new_entries)

    print(f"\n[ArSL] Done. {len(new_entries)} expression marker slots injected cleanly.\n")


if __name__ == "__main__":
    main()