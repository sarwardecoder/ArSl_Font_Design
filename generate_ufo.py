#!/usr/bin/env python3
"""Generate a fresh empty UFO from GlyphData.xml for ArSL font design."""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from ufoLib2 import Font
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: install ufoLib2 via `pip install ufoLib2`."
    ) from exc


def parse_glyph_data(xml_path):
    xml_path = Path(xml_path)
    if not xml_path.exists():
        raise FileNotFoundError(f"Glyph data XML file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    glyphs = []

    for glyph_elem in root.findall(".//Glyph"):
        index = glyph_elem.get("index")
        name = glyph_elem.get("name")
        code = glyph_elem.get("code")

        if not index or not name or not code:
            raise ValueError(
                f"Glyph entry missing required attributes: {ET.tostring(glyph_elem, encoding='unicode')}"
            )

        glyphs.append({
            "index": int(index, 10),
            "name": name,
            "pua_code": code.upper(),
        })

    glyphs.sort(key=lambda item: item["index"])
    return glyphs


def make_ufo(glyphs, output_path, arabic_start=0x0621):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    font = Font()
    font.info.familyName = "ArSL Base Shell"
    font.info.styleName = "Regular"
    font.info.unitsPerEm = 1000
    font.info.ascender = 800
    font.info.descender = -200

    glyph_order = []
    arabic_allocations = {}
    next_arabic = arabic_start

    for glyph in glyphs:
        glyph_name = glyph["name"]
        pua_value = int(glyph["pua_code"], 16)

        if next_arabic > 0x06FF:
            raise ValueError("Arabic code assignments exceeded the available Arabic block range.")

        ufo_glyph = font.newGlyph(glyph_name)
        ufo_glyph.width = 1000
        ufo_glyph.unicode = pua_value
        ufo_glyph.note = (
            f"PUA={glyph['pua_code']} "
            f"Arabic={next_arabic:04X}"
        )

        glyph_order.append(glyph_name)
        arabic_allocations[glyph_name] = f"{next_arabic:04X}"
        next_arabic += 1

    font.glyphOrder = glyph_order
    font.lib["com.sarwardecoder.arabicHexAllocations"] = arabic_allocations
    font.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate a UFO source from tools/GlyphData.xml for Arabic Sign Language."
    )
    parser.add_argument(
        "--glyph-data",
        default="tools/GlyphData.xml",
        help="Path to the GlyphData.xml matrix file.",
    )
    parser.add_argument(
        "--output-ufo",
        default="source/ArSL_Base_Shell.ufo",
        help="Destination UFO path to create.",
    )
    parser.add_argument(
        "--arabic-start",
        default="0621",
        help="Hex start for Arabic allocations (default: 0621).",
    )

    args = parser.parse_args()
    glyphs = parse_glyph_data(args.glyph_data)
    output_path = Path(args.output_ufo)
    arabic_start = int(args.arabic_start, 16)

    ufo_path = make_ufo(glyphs, output_path, arabic_start=arabic_start)
    print(f"Created UFO: {ufo_path}")
    print(f"Generated {len(glyphs)} glyphs with PUA and Arabic hex allocations.")


if __name__ == "__main__":
    main()
