import fitz
import os
import shutil
import re

# Directories
workspace_dir = r"c:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
subfolders = [
    os.path.join(workspace_dir, "Kova 3.5 - Cushion Adjustments 8.25", "ECO - D-20331 - Box"),
    os.path.join(workspace_dir, "Kova 3.5 - Cushion Adjustments 8.25", "ECO - D-20386 - Flange")
]
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# Clean out old crops inside the crops folder
print("Cleaning old crops...")
for f in os.listdir(crops_dir):
    try:
        os.remove(os.path.join(crops_dir, f))
    except Exception as e:
        pass

def add_seam_note(page):
    """Writes the large seam note on the drawing and adds a revision cloud."""
    # Text to write
    line1 = "THE SEAM OF THE DACRON (FIBER) WRAP TO BE"
    line2 = "LOCATED ON THE BOTTOM FACE OF THE CUSHION"
    
    # Coordinates (middle top)
    pos_line1 = fitz.Point(950, 130)
    pos_line2 = fitz.Point(950, 170)
    
    # Write text
    page.insert_text(pos_line1, line1, fontsize=24, fontname="hebo", color=(1, 0, 0))
    page.insert_text(pos_line2, line2, fontsize=24, fontname="hebo", color=(1, 0, 0))
    
    # Calculate bounding box for cloud
    line1_len = fitz.get_text_length(line1, fontname="hebo", fontsize=24)
    line2_len = fitz.get_text_length(line2, fontname="hebo", fontsize=24)
    max_len = max(line1_len, line2_len)
    
    # Bounding box with some padding
    cloud_rect = fitz.Rect(930, 90, 950 + max_len + 20, 190)
    
    # Add wavy revision cloud
    cloud = page.add_rect_annot(cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    
    return cloud_rect

def replace_dimension_with_cloud(page, rect, old_text, new_text, font_size=24, offset_y=-12):
    """Crosses out old dimension, writes new text, and clouds them."""
    y_mid = (rect.y0 + rect.y1) / 2.0
    
    # 1. Strike out old dimension
    shape = page.new_shape()
    shape.draw_line(fitz.Point(rect.x0 - 4, y_mid), fitz.Point(rect.x1 + 4, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # 2. Write new dimension above
    new_pos = fitz.Point(rect.x0, rect.y0 + offset_y)
    page.insert_text(new_pos, new_text, fontsize=font_size, fontname="hebo", color=(1, 0, 0))
    
    # 3. Cloud the area
    text_len = fitz.get_text_length(new_text, fontname="hebo", fontsize=font_size)
    cloud_rect = fitz.Rect(
        rect.x0 - 8,
        rect.y0 - font_size - 8,
        max(rect.x1, rect.x0 + text_len) + 8,
        rect.y1 + 4
    )
    cloud_rect = cloud_rect & page.rect
    cloud = page.add_rect_annot(cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    
    return cloud_rect

# Loop over subfolders and process each drawing
for folder in subfolders:
    print(f"\nScanning folder: {os.path.basename(folder)}")
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".pdf") or "redlines" in filename.lower():
            continue
            
        src_path = os.path.join(folder, filename)
        
        # Extract part number
        part_no_match = re.match(r"^(\d{2}-\d{6})", filename)
        if not part_no_match:
            print(f"Skipping unrecognized file: {filename}")
            continue
        part_no = part_no_match.group(1)
        
        # Back up original file if not already backed up
        backup_path = os.path.join(backup_dir, filename)
        if not os.path.exists(backup_path):
            print(f"  Backing up {filename} to {backup_path}...")
            shutil.copy2(src_path, backup_path)
        
        print(f"  Processing {filename} (Part: {part_no})...")
        
        # Open backed-up clean file
        doc = fitz.open(backup_path)
        page = doc[0]
        
        crops_to_save = [] # list of (label, rect)
        
        # Determine if it's a Foam Core drawing
        is_foam_core = part_no in ["93-027231", "93-027238"]
        
        if is_foam_core:
            # size adjustmetns noted are only applied to the foam cores (parts 238 and 231)
            # Find and replace "825.5" with "831.9" (both occurrences on page)
            rects = page.search_for("825.5")
            print(f"    Found {len(rects)} occurrences of '825.5'")
            for idx, r in enumerate(rects):
                c_rect = replace_dimension_with_cloud(page, r, "825.5", "831.9")
                crops_to_save.append((f"size_change_{idx}", c_rect))
                print(f"    Replaced '825.5' -> '831.9' at {r}")
        else:
            # Mark seam position change on assembly drawings and fiber drawings
            # Write large note at top-middle area
            c_rect = add_seam_note(page)
            crops_to_save.append(("seam_note", c_rect))
            print("    Added Dacron wrap seam note.")
            
        # Revision letter crop for verification (x: 2330-2440, y: 1460-1540)
        crops_to_save.append(("rev_letter", fitz.Rect(2330, 1460, 2440, 1540)))
        
        # Save output PDF
        out_filename = f"{part_no} redlines.pdf"
        out_path = os.path.join(folder, out_filename)
        doc.save(out_path)
        doc.close()
        print(f"    Saved redlined drawing: {out_path}")
        
        # Remove original clean file from folder
        if os.path.exists(src_path) and src_path != out_path:
            os.remove(src_path)
            print(f"    Removed original {filename} from folder")
            
        # Render visual crops
        doc_ver = fitz.open(out_path)
        p0_ver = doc_ver[0]
        for label, rect in crops_to_save:
            pad = 20
            crop_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
            crop_rect = crop_rect & p0_ver.rect
            pix = p0_ver.get_pixmap(clip=crop_rect, matrix=fitz.Matrix(2, 2))
            crop_file = os.path.join(crops_dir, f"{part_no}_{label}.png")
            pix.save(crop_file)
            print(f"    Saved verification crop: {crop_file}")
        doc_ver.close()

print("\nAll adjustments processed successfully!")
