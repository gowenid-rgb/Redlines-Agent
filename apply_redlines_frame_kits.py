import fitz
import os
import shutil

# Directories
workspace_dir = r"C:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
subfolder_name = "Kova 3.5 - Frame Kits"
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

def draw_redline_text(page, rect, new_text, font_size=14, offset_y=-2):
    """
    Cross out the text at rect, write new_text in red bold above it,
    and add a revision cloud surrounding both.
    """
    y_mid = (rect.y0 + rect.y1) / 2.0
    
    # 1. Draw cross-out line
    shape = page.new_shape()
    shape.draw_line(fitz.Point(rect.x0 - 4, y_mid), fitz.Point(rect.x1 + 4, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # 2. Write new text
    new_pos = fitz.Point(rect.x0, rect.y0 + offset_y)
    page.insert_text(new_pos, new_text, fontsize=font_size, fontname="hebo", color=(1, 0, 0))
    
    # 3. Calculate cloud rectangle
    text_len = fitz.get_text_length(new_text, fontname="hebo", fontsize=font_size)
    cloud_rect = fitz.Rect(
        rect.x0 - 8,
        rect.y0 - font_size - 4,
        max(rect.x1, rect.x0 + text_len) + 8,
        rect.y1 + 4
    )
    cloud_rect = cloud_rect & page.rect
    
    # 4. Add revision cloud
    cloud = page.add_rect_annot(cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    
    return cloud_rect

# ==================== 1. Process 92-019429 (Ottoman Kit) ====================
filename_9429 = "92-019429 REV A P-02.pdf"
src_path_9429 = os.path.join(folder_path, filename_9429)
backup_path_9429 = os.path.join(backup_dir, filename_9429)

print(f"\nProcessing {filename_9429}...")
# Backup
if os.path.exists(src_path_9429) and not os.path.exists(backup_path_9429):
    print(f"Backing up to {backup_path_9429}...")
    shutil.copy2(src_path_9429, backup_path_9429)

doc_9429 = fitz.open(backup_path_9429)
page_9429 = doc_9429[0]
crops_9429 = []

# Find quantity '3' for 92-026564 (BOM row y ~276)
rects = page_9429.search_for("3")
target_rect = None
for r in rects:
    # Filter for target box x ~580, y ~276
    if 570 < r.x0 < 590 and 270 < r.y0 < 285:
        target_rect = r
        break

if not target_rect:
    raise ValueError("Could not find the Ganging Spacer Qty '3' rect on page.")

c_rect = draw_redline_text(page_9429, target_rect, "4", font_size=16, offset_y=-2)
crops_9429.append(("qty_correction", c_rect))

# Title block revision letter (x: 2340-2440, y: 1470-1540)
crops_9429.append(("rev_letter", fitz.Rect(2340, 1470, 2440, 1540)))

out_path_9429 = os.path.join(folder_path, "92-019429 redlines.pdf")
doc_9429.save(out_path_9429)
doc_9429.close()
print(f"Saved {out_path_9429}")


# ==================== 2. Process 92-023777 (Arm Chair Kit) ====================
filename_3777 = "92-023777 REV A P-01 (1).pdf"
src_path_3777 = os.path.join(folder_path, filename_3777)
backup_path_3777 = os.path.join(backup_dir, filename_3777)

print(f"\nProcessing {filename_3777}...")
# Backup
if os.path.exists(src_path_3777) and not os.path.exists(backup_path_3777):
    print(f"Backing up to {backup_path_3777}...")
    shutil.copy2(src_path_3777, backup_path_3777)

doc_3777 = fitz.open(backup_path_3777)
page_3777 = doc_3777[0]
crops_3777 = []

# Find part number '92-023437' (BOM row y ~174)
rects = page_3777.search_for("92-023437")
if not rects:
    raise ValueError("Could not find part number '92-023437' rect on page.")

c_rect = draw_redline_text(page_3777, rects[0], "92-020147", font_size=12, offset_y=-2)
crops_3777.append(("pn_correction", c_rect))

# Title block revision letter (x: 2340-2440, y: 1470-1540)
crops_3777.append(("rev_letter", fitz.Rect(2340, 1470, 2440, 1540)))

out_path_3777 = os.path.join(folder_path, "92-023777 redlines.pdf")
doc_3777.save(out_path_3777)
doc_3777.close()
print(f"Saved {out_path_3777}")


# ==================== Render validation crops ====================
print("\nRendering verification crops...")

def save_crops(doc_name, filename, crops_list):
    doc = fitz.open(os.path.join(folder_path, filename))
    page = doc[0]
    for label, rect in crops_list:
        pad = 25
        crop_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
        crop_rect = crop_rect & page.rect
        
        pix = page.get_pixmap(clip=crop_rect, matrix=fitz.Matrix(2, 2))
        crop_file = os.path.join(crops_dir, f"{doc_name}_{label}.png")
        pix.save(crop_file)
        print(f"  Saved verification crop: {crop_file}")
    doc.close()

save_crops("92-019429", "92-019429 redlines.pdf", crops_9429)
save_crops("92-023777", "92-023777 redlines.pdf", crops_3777)

# Remove original clean files from the subfolder
if os.path.exists(src_path_9429):
    os.remove(src_path_9429)
    print(f"Removed original {filename_9429}")
if os.path.exists(src_path_3777):
    os.remove(src_path_3777)
    print(f"Removed original {filename_3777}")

print("\nRedlining complete! Visual crop validation images generated in 'crops' directory.")
