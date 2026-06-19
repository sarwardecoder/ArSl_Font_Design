import os
import xml.etree.ElementTree as ET
from fontTools.ufoLib.glifLib import GlyphSet

def inject_placeholder_vectors(ufo_path):
    glyphs_dir = os.path.join(ufo_path, 'glyphs')
    contents_plist_path = os.path.join(glyphs_dir, 'contents.plist')
    
    if not os.path.exists(contents_plist_path):
        print(f"Error: {contents_plist_path} does not exist. Run generate_ufo.py first.")
        return

    # Open the existing glyph set mapping
    glyph_set = GlyphSet(glyphs_dir)
    
    # Define a simple, clean test square boundary matrix (200x200 units) to inject as a placeholder
    # This proves the rendering engines can draw our shapes correctly.
   # An explicitly closed vector loop format that passes compiler rules smoothly
    test_contour = """
    <contour>
      <point x="200" y="0" type="line"/>
      <point x="200" y="200" type="line"/>
      <point x="400" y="200" type="line"/>
      <point x="400" y="0" type="line"/>
    </contour>
    """
    contour_element = ET.fromstring(test_contour)

    print("Beginning programmatic vector injection into 60 slots...")
    
    # Iterate through all glyphs registered in our UFO directory
    for glyph_name in glyph_set.contents.keys():
        # Load the raw structural GLIF file data
        glif_path = os.path.join(glyphs_dir, glyph_set.contents[glyph_name])
        
        tree = ET.parse(glif_path)
        root = tree.getroot()
        
        # Find or create the outline element block inside the .glif structural code
        outline = root.find('outline')
        if outline is None:
            outline = ET.SubElement(root, 'outline')
        
        # Clear out any previous paths to avoid duplication errors
        outline.clear()
        
        # Append our vector points dynamically
        outline.append(contour_element)
        
        # Save the updated vector data right back to the file branch
        tree.write(glif_path, encoding='UTF-8', xml_declaration=True)
        print(f" Injected vector path matrix cleanly into -> {glyph_name}")

if __name__ == "__main__":
    ufo_target = "source/ArSL_Base_Shell.ufo"
    inject_placeholder_vectors(ufo_target)