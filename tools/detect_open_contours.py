#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
import sys

ufo_dir = "source/ArSL_Base_Shell.ufo"  # adjust if your UFO path is different
glyphs_dir = os.path.join(ufo_dir, "glyphs")
if not os.path.isdir(glyphs_dir):
    print("ERROR: glyphs/ directory not found:", glyphs_dir)
    sys.exit(2)

found = False
for fname in sorted(os.listdir(glyphs_dir)):
    if not fname.endswith(".glif"):
        continue
    path = os.path.join(glyphs_dir, fname)
    try:
        tree = ET.parse(path)
    except Exception as e:
        print("Failed to parse", path, ":", e)
        continue
    root = tree.getroot()
    for contour in root.findall(".//contour"):
        open_attr = contour.get("open")
        if open_attr and open_attr.lower() in ("1","true"):
            print(f"OPEN CONTOUR: {fname} (open=\"{open_attr}\")")
            found = True

if not found:
    print("No explicit open contours found.")
    sys.exit(0)
else:
    print("Review the listed .glif files before applying any automated fix.")
    sys.exit(1)