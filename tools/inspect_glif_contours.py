#!/usr/bin/env python3
"""
Inspect GLIF contours for likely causes of "Unhandled open contour":
- contours with zero points
- first or last point marked as offcurve
- point missing x/y attributes
Usage:
  python3 tools/inspect_glif_contours.py
  python3 tools/inspect_glif_contours.py --glyph ASL_001
"""
import os, xml.etree.ElementTree as ET, argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument("--ufo", default="source/ArSL_Base_Shell.ufo", help="UFO directory")
parser.add_argument("--glyph", default=None, help="Glyph name (filename without .glif) to inspect")
args = parser.parse_args()

glyphs_dir = os.path.join(args.ufo, "glyphs")
if not os.path.isdir(glyphs_dir):
    print("ERROR: glyphs/ directory not found:", glyphs_dir)
    sys.exit(2)

def inspect_file(path):
    try:
        tree = ET.parse(path)
    except Exception as e:
        print(f"PARSE ERROR: {path}: {e}")
        return
    root = tree.getroot()
    issues = []
    for i, contour in enumerate(root.findall(".//contour")):
        pts = []
        for pt in contour.findall("point"):
            pts.append({
                "x": pt.get("x"),
                "y": pt.get("y"),
                "type": pt.get("type")
            })
        if len(pts) == 0:
            issues.append(f"  contour[{i}]: ZERO points")
            continue
        first, last = pts[0], pts[-1]
        if first["x"] is None or first["y"] is None:
            issues.append(f"  contour[{i}]: first point missing x/y -> {first}")
        if last["x"] is None or last["y"] is None:
            issues.append(f"  contour[{i}]: last point missing x/y -> {last}")
        # offcurve detection - some fonts use type='offcurve'
        if (first.get("type") or "").lower() == "offcurve":
            issues.append(f"  contour[{i}]: first point is OFFCURVE -> {first}")
        if (last.get("type") or "").lower() == "offcurve":
            issues.append(f"  contour[{i}]: last point is OFFCURVE -> {last}")
        # unexpected missing 'type' can be suspicious if many points have no type
        none_type_count = sum(1 for p in pts if p.get("type") is None)
        if none_type_count == len(pts):
            issues.append(f"  contour[{i}]: ALL points missing type attribute (could be malformed)")
        if none_type_count > 0 and none_type_count < len(pts):
            issues.append(f"  contour[{i}]: some points missing type attribute ({none_type_count}/{len(pts)})")
    if issues:
        print(f"Issues in {os.path.basename(path)}:")
        for s in issues:
            print(s)
        print()
    return

files = sorted([f for f in os.listdir(glyphs_dir) if f.endswith(".glif")])
if args.glyph:
    target = args.glyph if args.glyph.endswith(".glif") else args.glyph + ".glif"
    if target not in files:
        print("Glyph file not found:", target); sys.exit(1)
    inspect_file(os.path.join(glyphs_dir, target))
else:
    for fn in files:
        inspect_file(os.path.join(glyphs_dir, fn))