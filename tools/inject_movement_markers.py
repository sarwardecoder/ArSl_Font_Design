"""
tools/inject_movement_markers.py
ArSL Font Project — Agent 2: OpenType Logic & Scripting Engineer

Injects placeholder stroke vector coordinates (arrow/path geometry)
into movement track slots ASL_029 through ASL_040.
Each slot receives a unique diagonal vector path to compile as a
distinct glyph contour without hand component layer dependencies.
"""

from fontTools.pens.t2Pen import T2Pen
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools import ttLib
import os

# ── Slot definitions: ASL_029 → ASL_040 ──────────────────────────────────────
# Each entry: (glyph_name, unicode_codepoint, x1, y1, x2, y2)
# Diagonal vector offsets are staggered per slot to produce unique paths.

MOVEMENT_SLOTS = [
    ("ASL_029", 0xE029, 100, 100, 500, 500),
    ("ASL_030", 0xE030, 120, 100, 520, 500),
    ("ASL_031", 0xE031, 140, 100, 540, 500),
    ("ASL_032", 0xE032, 160, 100, 560, 500),
    ("ASL_033", 0xE033, 180, 100, 580, 500),
    ("ASL_034", 0xE034, 200, 100, 600, 500),
    ("ASL_035", 0xE035, 220, 100, 620, 500),
    ("ASL_036", 0xE036, 240, 100, 640, 500),
    ("ASL_037", 0xE037, 260, 100, 660, 500),
    ("ASL_038", 0xE038, 280, 100, 680, 500),
    ("ASL_039", 0xE039, 300, 100, 700, 500),
    ("ASL_040", 0xE040, 320, 100, 720, 500),
]

STROKE_WIDTH   = 40   # pen nib half-width for stroke expansion
UNITS_PER_EM   = 1000
ASCENDER       = 800
DESCENDER      = -200
OUTPUT_DIR     = os.path.join(os.path.dirname(__file__), "..", "build")
OUTPUT_TTF     = os.path.join(OUTPUT_DIR, "ArSL_movement_markers.ttf")


def stroke_contour(pen, x1, y1, x2, y2, half_w=STROKE_WIDTH):
    """
    Expand a single diagonal vector (x1,y1)→(x2,y2) into a closed
    rectangular stroke contour approximating an arrow shaft.
    """
    dx, dy = x2 - x1, y2 - y1
    length  = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return
    nx, ny  = -dy / length * half_w, dx / length * half_w

    # Four corners of the stroke rectangle
    p0 = (x1 + nx, y1 + ny)
    p1 = (x2 + nx, y2 + ny)
    p2 = (x2 - nx, y2 - ny)
    p3 = (x1 - nx, y1 - ny)

    pen.moveTo(p0)
    pen.lineTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.closePath()


def arrowhead_contour(pen, x1, y1, x2, y2, tip_size=60):
    """
    Draw a filled triangular arrowhead at the terminal point (x2, y2).
    """
    dx, dy = x2 - x1, y2 - y1
    length  = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return
    ux, uy  =  dx / length,  dy / length
    px, py  = -uy * tip_size * 0.5, ux * tip_size * 0.5

    tip   = (x2, y2)
    base1 = (x2 - ux * tip_size + px, y2 - uy * tip_size + py)
    base2 = (x2 - ux * tip_size - px, y2 - uy * tip_size - py)

    pen.moveTo(tip)
    pen.lineTo(base1)
    pen.lineTo(base2)
    pen.closePath()


def build_movement_font():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fb = FontBuilder(UNITS_PER_EM, isTTF=True)
    fb.setupGlyphOrder([".notdef"] + [s[0] for s in MOVEMENT_SLOTS])
    fb.setupCharacterMap({s[1]: s[0] for s in MOVEMENT_SLOTS})

    fb.setupGlyf({})          # populated below via RecordingPen round-trip
    fb.setupHorizontalMetrics({
        ".notdef": (500, 0),
        **{s[0]: (s[4] + STROKE_WIDTH + 20, 0) for s in MOVEMENT_SLOTS},
    })

    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)
    fb.setupNameTable({
        "familyName":     "ArSL Movement Markers",
        "styleName":      "Regular",
        "fullName":       "ArSL Movement Markers Regular",
        "version":        "Version 1.0",
        "psName":         "ArSLMovementMarkers-Regular",
        "uniqueFontIdentifier": "ArSL:MovementMarkers:2025",
    })
    fb.setupOs2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        fsType=0x0004,
        achVendID="ARSL",
    )
    fb.setupPost()
    fb.setupHead(unitsPerEm=UNITS_PER_EM)

    # ── Build glyph outlines ──────────────────────────────────────────────────
    glyphs     = {}
    glyph_set  = {}

    # .notdef — empty 500-unit box
    rp = RecordingPen()
    rp.moveTo((50, 0))
    rp.lineTo((450, 0))
    rp.lineTo((450, 700))
    rp.lineTo((50, 700))
    rp.closePath()
    glyph_set[".notdef"] = rp

    for name, cp, x1, y1, x2, y2 in MOVEMENT_SLOTS:
        rp = RecordingPen()
        stroke_contour(rp, x1, y1, x2, y2)
        arrowhead_contour(rp, x1, y1, x2, y2)
        glyph_set[name] = rp

    # Inject recorded contours into the glyf table
    font = fb.font
    glyf_table = font["glyf"]
    for gname, rec_pen in glyph_set.items():
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        tt_pen = TTGlyphPen(None)
        rec_pen.replay(tt_pen)
        glyf_table[gname] = tt_pen.glyph()

    font.save(OUTPUT_TTF)
    print(f"[ArSL] Movement marker font written → {OUTPUT_TTF}")
    print(f"[ArSL] Slots compiled: {', '.join(s[0] for s in MOVEMENT_SLOTS)}")


if __name__ == "__main__":
    build_movement_font()