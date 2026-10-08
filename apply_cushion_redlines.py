import fitz
import os
import shutil
import re

workspace_dir = r"c:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
subfolder_name = "Kova 3.5 - Cushion size removal and firm update"
folder_path = os.path.join(workspace_dir, subfolder_name)
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# Clean out old crops
for f in os.listdir(crops_dir):
    try:
        os.remove(os.path.join(crops_dir, f))
    except Exception:
        pass

# List files
files = sorted(os.listdir(folder_path))

# Regex for matching size dimensions in descriptions/BOMs
size_regex = re.compile(
    r"\b(3[0-3]\s*[xX]\s*3[0-3]|\b[34](\.5)?\s*(?:in|IN)\b)",
    re.IGNORECASE
)

def strike_and_cloud(page, rect):
    """Draw red cross-out line and revision cloud around a rect."""
    y_mid = (rect.y0 + rect.y1) / 2.0
    shape = page.new_shape()
    shape.draw_line(fitz.Point(rect.x0 - 4, y_mid), fitz.Point(rect.x1 + 4, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # Add revision cloud
    cloud_rect = fitz.Rect(rect.x0 - 6, rect.y0 - 4, rect.x1 + 6, rect.y1 + 4)
    cloud_rect = cloud_rect & page.rect
    cloud = page.add_rect_annot(cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    return cloud_rect

def replace_and_cloud(page, rect, new_text, font_size=24, offset_y=-10):
    """Cross out a rect, write new text above it in red bold, and cloud both."""
    y_mid = (rect.y0 + rect.y1) / 2.0
    shape = page.new_shape()
    shape.draw_line(fitz.Point(rect.x0 - 4, y_mid), fitz.Point(rect.x1 + 4, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # Write new text above
    new_pos = fitz.Point(rect.x0, rect.y0 + offset_y)
    page.insert_text(new_pos, new_text, fontsize=font_size, fontname="hebo", color=(1, 0, 0))
    
    # Calculate combined bounding box for the cloud
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

for filename in files:
    if not filename.lower().endswith(".pdf"):
        continue
        
    src_path = os.path.join(folder_path, filename)
    
    # Extract part number from filename
    part_no_match = re.match(r"^(\d{2}-\d{6})", filename)
    if not part_no_match:
        print(f"Skipping file with unrecognized part number: {filename}")
        continue
    part_no = part_no_match.group(1)
    
    # Backup clean original
    backup_path = os.path.join(backup_dir, filename)
    if not os.path.exists(backup_path):
        print(f"Backing up {filename}...")
        shutil.copy2(src_path, backup_path)
        
    print(f"\nProcessing {filename}...")
    doc = fitz.open(backup_path)
    page = doc[0]
    
    crops_to_save = [] # List of (label, rect)
    
    # --- 1. Strike out Size/Dimensions in Title Block and BOM ---
    text = page.get_text()
    matches = list(size_regex.finditer(text))
    
    matched_strings = sorted(list(set(m.group(0) for m in matches)), key=len, reverse=True)
    
    for m_str in matched_strings:
        rects = page.search_for(m_str)
        for rect in rects:
            # Exclude Notes area (bottom left, x < 1400, y > 1200) unless it is y < 400 (BOM area)
            if rect.x0 < 1400 and rect.y0 > 1200:
                if rect.y0 > 400:
                    continue
            
            c_rect = strike_and_cloud(page, rect)
            label = f"size_strike_{int(rect.x0)}_{int(rect.y0)}"
            crops_to_save.append((label, c_rect))
            print(f"  Struck size '{m_str}' at {[round(x,1) for x in rect]}")

    # --- 2. Handle Spec updates for Firm Core Foams ---
    if part_no == "93-027228":
        spec_headers = page.search_for("DENSITY:")
        for r in spec_headers:
            if r.x0 > 1700 and r.y0 > 1300:
                spec_line_rect = fitz.Rect(r.x0, r.y0 - 2, 2020.0, r.y1 + 2)
                new_spec = "DENSITY: 2.5 lb/ft³, IFD: 42 HR"
                c_rect = replace_and_cloud(page, spec_line_rect, new_spec, font_size=24, offset_y=-12)
                crops_to_save.append(("spec_update", c_rect))
                print(f"  Updated core spec to Firm for 93-027228")
                break

    # --- 3. Handle BOM Correction for Firm Assembly (93-027227) ---
    if part_no == "93-027227":
        soft_rects = page.search_for("SOFT")
        for r in soft_rects:
            if r.x0 < 1000 and r.y0 < 400:
                c_rect = replace_and_cloud(page, r, "FIRM", font_size=24, offset_y=-12)
                crops_to_save.append(("bom_soft_to_firm", c_rect))
                print(f"  Corrected SOFT to FIRM in 93-027227 BOM")
                break

    # --- 4. Handle Core Foam Exceptions from user Double Check ---
    # Exception A: 93-020191 (Soft Core) needs thickness redline from 88.90 -> 101.60
    if part_no == "93-020191":
        thickness_rects = page.search_for("88.90")
        for r in thickness_rects:
            if r.x0 < 1700 and r.y0 < 1200: # drawing area
                c_rect = replace_and_cloud(page, r, "101.60", font_size=24, offset_y=-12)
                crops_to_save.append(("thickness_update", c_rect))
                print(f"  Updated soft core thickness from 88.90 to 101.60 (93-020191)")
                break

    # Exception B: 93-027231 (Soft Core) needs spec block redline from 1.8 -> 2.0/24HR
    if part_no == "93-027231":
        spec_headers = page.search_for("DENSITY:")
        for r in spec_headers:
            if r.x0 > 1700 and r.y0 > 1300:
                spec_line_rect = fitz.Rect(r.x0, r.y0 - 2, 2020.0, r.y1 + 2)
                new_spec = "DENSITY: 2.0 lb/ft³, IFD: 24 HR"
                c_rect = replace_and_cloud(page, spec_line_rect, new_spec, font_size=24, offset_y=-12)
                crops_to_save.append(("spec_update", c_rect))
                print(f"  Updated soft core spec to 2.0/24 HR (93-027231)")
                break

    # Exception C: 93-027238 (Soft Core) needs spec block redline from 1.8 -> 2.0/24HR
    if part_no == "93-027238":
        spec_headers = page.search_for("DENSITY:")
        for r in spec_headers:
            if r.x0 > 1700 and r.y0 > 1300:
                spec_line_rect = fitz.Rect(r.x0, r.y0 - 2, 2020.0, r.y1 + 2)
                new_spec = "DENSITY: 2.0 lb/ft³, IFD: 24 HR"
                c_rect = replace_and_cloud(page, spec_line_rect, new_spec, font_size=24, offset_y=-12)
                crops_to_save.append(("spec_update", c_rect))
                print(f"  Updated soft core spec to 2.0/24 HR (93-027238)")
                break

    # Save output
    out_filename = f"{part_no} redlines.pdf"
    out_path = os.path.join(folder_path, out_filename)
    doc.save(out_path)
    doc.close()
    print(f"Saved {out_path}")
    
    # Remove clean file from workspace
    if os.path.exists(src_path) and src_path != out_path:
        os.remove(src_path)
        print(f"Removed original {filename}")

    # Generate crops for visual verification
    doc_ver = fitz.open(out_path)
    p0_ver = doc_ver[0]
    for label, rect in crops_to_save:
        pad = 25
        crop_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
        crop_rect = crop_rect & p0_ver.rect
        pix = p0_ver.get_pixmap(clip=crop_rect, matrix=fitz.Matrix(2, 2))
        crop_file = os.path.join(crops_dir, f"{part_no}_{label}.png")
        pix.save(crop_file)
    doc_ver.close()

print("\nAll drawing redlines and double-check rules successfully updated!")
