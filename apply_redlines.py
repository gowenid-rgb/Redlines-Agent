import fitz
import os
import shutil

# Directories
workspace_dir = r"C:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

if os.path.exists(crops_dir):
    for f in os.listdir(crops_dir):
        try:
            os.remove(os.path.join(crops_dir, f))
        except Exception:
            pass
else:
    os.makedirs(crops_dir, exist_ok=True)

# List of files to process
drawings = [
    "93-020190 REV A.pdf",
    "93-020191 REV A.pdf",
    "93-020192 REV A.pdf"
]

# Backup files first if not already backed up
for d in drawings:
    src_path = os.path.join(workspace_dir, d)
    dst_path = os.path.join(backup_dir, d)
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        print(f"Backing up {d} to {dst_path}...")
        shutil.copy2(src_path, dst_path)

def draw_redline_text(page, search_term, new_text, occ_idx=0, font_size=14, offset_y=-2, is_spec=False):
    """
    Search for search_term, cross it out in red, and write new_text above it.
    Also adds a revision cloud surrounding both.
    """
    rects = page.search_for(search_term)
    if not rects:
        raise ValueError(f"Term '{search_term}' not found on page.")
    if occ_idx >= len(rects):
        raise ValueError(f"Occurrence index {occ_idx} out of range for term '{search_term}' (found {len(rects)}).")
    
    rect = rects[occ_idx]
    y_mid = (rect.y0 + rect.y1) / 2.0
    
    # 1. Draw cross-out line
    shape = page.new_shape()
    shape.draw_line(fitz.Point(rect.x0 - 4, y_mid), fitz.Point(rect.x1 + 4, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # 2. Write new text & compute cloud rect
    if is_spec:
        new_pos = fitz.Point(1860.0, 1374.0)
        page.insert_text(new_pos, new_text, fontsize=9, fontname="hebo", color=(1, 0, 0))
        # Specification cloud coordinates from Rules.md
        cloud_rect = fitz.Rect(rect.x0 - 15, 1352.0, rect.x1 + 15, rect.y1 + 10)
    else:
        new_pos = fitz.Point(rect.x0, rect.y0 + offset_y)
        page.insert_text(new_pos, new_text, fontsize=font_size, fontname="hebo", color=(1, 0, 0))
        
        # Calculate cloud rectangle
        text_len = fitz.get_text_length(new_text, fontname="hebo", fontsize=font_size)
        cloud_rect = fitz.Rect(
            min(rect.x0, rect.x0) - 8,
            rect.y0 - font_size - 4,
            max(rect.x1, rect.x0 + text_len) + 8,
            rect.y1 + 4
        )
    
    # 3. Add revision cloud
    cloud = page.add_rect_annot(cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    
    return rect, cloud_rect

# ==================== Process 93-020190 (Assembly) ====================
print("\nProcessing 93-020190...")
doc_90 = fitz.open(os.path.join(backup_dir, "93-020190 REV A.pdf"))
page_90 = doc_90[0]
crops_90 = []

# Change 1: Thickness dimension 126.9 -> 139.6
r, c = draw_redline_text(page_90, "126.9", "139.6", font_size=14)
crops_90.append(("thickness", c))

# Change 2: Title Block Title SOFT -> MEDIUM (second occurrence of SOFT on the page)
r, c = draw_redline_text(page_90, "SOFT", "MEDIUM", occ_idx=1, font_size=16)
crops_90.append(("title_soft", c))

# Change 3: BOM Item 1 description SOFT -> MEDIUM (first occurrence of SOFT on the page)
r, c = draw_redline_text(page_90, "SOFT", "MEDIUM", occ_idx=0, font_size=10)
crops_90.append(("bom_soft", c))

# Change 4: BOM Item 2 description 3.5in -> 4.0in
r, c = draw_redline_text(page_90, "3.5in", "4.0in", font_size=10)
crops_90.append(("bom_wrap", c))

# Change 5: Title Block Revision letter verification crop (x: 2360-2400, y: 1470-1530)
crops_90.append(("rev_letter", fitz.Rect(2360, 1470, 2400, 1530)))

doc_90.save(os.path.join(workspace_dir, "93-020190 redlines.pdf"))
doc_90.close()


# ==================== Process 93-020191 (Cushion Foam) ====================
print("\nProcessing 93-020191...")
doc_91 = fitz.open(os.path.join(backup_dir, "93-020191 REV A.pdf"))
page_91 = doc_91[0]
crops_91 = []

# Change 1: Thickness dimension 88.90 -> 101.6
r, c = draw_redline_text(page_91, "88.90", "101.6", font_size=14)
crops_91.append(("thickness", c))

# Change 2: Title Block Title SOFT -> MEDIUM
r, c = draw_redline_text(page_91, "SOFT", "MEDIUM", font_size=16)
crops_91.append(("title_soft", c))

# Change 3: Specification Block DENSITY: 2.0lb/ft³ -> 2.5 lb/ft³
r, c = draw_redline_text(page_91, "DENSITY", "DENSITY: 2.5 lb/ft³, IFD: 24 HR", occ_idx=2, is_spec=True)
crops_91.append(("spec_block", c))

# Change 4: Title Block Revision letter verification crop (x: 2360-2400, y: 1470-1530)
crops_91.append(("rev_letter", fitz.Rect(2360, 1470, 2400, 1530)))

doc_91.save(os.path.join(workspace_dir, "93-020191 redlines.pdf"))
doc_91.close()


# ==================== Process 93-020192 (Dacron Wrap) ====================
print("\nProcessing 93-020192...")
doc_92 = fitz.open(os.path.join(backup_dir, "93-020192 REV A.pdf"))
page_92 = doc_92[0]
crops_92 = []

# List of dimension changes: (old_text, new_text, occ_idx)
wrap_dim_changes = [
    ("1896.6", "1918.6", 0),
    ("103.5", "114.5", 1),     # Top left notch depth
    ("103.5", "114.5", 0),     # Bottom left notch depth
    ("955.6", "966.6", 0),     # Bottom right section width (corrected to 966.6)
    ("1044.5", "1066.5", 0)    # Right section height
]

for idx, (old, new, occ) in enumerate(wrap_dim_changes):
    r, c = draw_redline_text(page_92, old, new, occ_idx=occ, font_size=14)
    crops_92.append((f"dim_{old}_{new}_{idx}", c))

# Title Block Revision letter verification crop (x: 2360-2400, y: 1470-1530)
crops_92.append(("rev_letter", fitz.Rect(2360, 1470, 2400, 1530)))

doc_92.save(os.path.join(workspace_dir, "93-020192 redlines.pdf"))
doc_92.close()


# ==================== Render validation crops ====================
print("\nRendering verification crops...")

def save_crops(doc_name, filename, crops_list):
    doc = fitz.open(os.path.join(workspace_dir, filename))
    page = doc[0]
    for label, rect in crops_list:
        # Add padding to crop area
        pad = 20
        crop_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
        # Ensure within bounds
        crop_rect = crop_rect & page.rect
        
        pix = page.get_pixmap(clip=crop_rect, matrix=fitz.Matrix(2, 2)) # zoom in
        crop_file = os.path.join(crops_dir, f"{doc_name}_{label}.png")
        pix.save(crop_file)
        print(f"  Saved verification crop: {crop_file}")
    doc.close()

save_crops("93-020190", "93-020190 redlines.pdf", crops_90)
save_crops("93-020191", "93-020191 redlines.pdf", crops_91)
save_crops("93-020192", "93-020192 redlines.pdf", crops_92)

# Remove original files from main workspace
for d in drawings:
    original_path = os.path.join(workspace_dir, d)
    if os.path.exists(original_path):
        print(f"Removing original file from workspace: {d}")
        os.remove(original_path)

print("\nRedlining complete! Visual crop validation images generated in 'crops' directory.")
