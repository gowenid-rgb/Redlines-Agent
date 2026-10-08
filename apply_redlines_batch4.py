import fitz
import os
import shutil

# Directories
workspace_dir = r"C:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# List of drawings to process
drawings = [
    "93-027227 REV A P-01.PDF",
    "93-027228 REV A P-01.PDF"
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

# ==================== 1. Process 93-027227 (Firm Assembly) ====================
print("\nProcessing 93-027227...")
doc_27 = fitz.open(os.path.join(backup_dir, "93-027227 REV A P-01.PDF"))
page_27 = doc_27[0]
crops_27 = []

# Change 1: BOM Item 1 description SOFT -> FIRM
r, c = draw_redline_text(page_27, "SOFT", "FIRM", occ_idx=0, font_size=10)
crops_27.append(("bom_soft_to_firm", c))

# Title Block Revision letter verification crop (x: 2360-2400, y: 1470-1530)
crops_27.append(("rev_letter", fitz.Rect(2360, 1470, 2400, 1530)))

doc_27.save(os.path.join(workspace_dir, "93-027227 redlines.pdf"))
doc_27.close()


# ==================== 2. Process 93-027228 (Firm core foam) ====================
print("\nProcessing 93-027228...")
doc_28 = fitz.open(os.path.join(backup_dir, "93-027228 REV A P-01.PDF"))
page_28 = doc_28[0]
crops_28 = []

# Change 1: Title Line 1 "4in, 33x33, SEAT" -> "33X33 SEAT CUSHION"
r, c = draw_redline_text(page_28, "4in, 33x33, SEAT", "33X33 SEAT CUSHION", font_size=16)
crops_28.append(("title_line1", c))

# Change 2: Title Line 2 "CUSHION FOAM" -> "CORE, FIRM"
r, c = draw_redline_text(page_28, "CUSHION FOAM", "CORE, FIRM", font_size=16)
crops_28.append(("title_line2", c))

# Title Block Revision letter verification crop (x: 2360-2400, y: 1470-1530)
crops_28.append(("rev_letter", fitz.Rect(2360, 1470, 2400, 1530)))

doc_28.save(os.path.join(workspace_dir, "93-027228 redlines.pdf"))
doc_28.close()


# ==================== Render validation crops ====================
print("\nRendering verification crops...")

def save_crops(doc_name, filename, crops_list):
    doc = fitz.open(os.path.join(workspace_dir, filename))
    page = doc[0]
    for label, rect in crops_list:
        pad = 20
        crop_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
        crop_rect = crop_rect & page.rect
        
        pix = page.get_pixmap(clip=crop_rect, matrix=fitz.Matrix(2, 2))
        crop_file = os.path.join(crops_dir, f"{doc_name}_{label}.png")
        pix.save(crop_file)
        print(f"  Saved verification crop: {crop_file}")
    doc.close()

save_crops("93-027227", "93-027227 redlines.pdf", crops_27)
save_crops("93-027228", "93-027228 redlines.pdf", crops_28)

# Remove original clean files from main workspace
for d in drawings:
    original_path = os.path.join(workspace_dir, d)
    if os.path.exists(original_path):
        print(f"Removing original file from workspace: {d}")
        os.remove(original_path)

print("\nRedlining complete! Visual crop validation images generated in 'crops' directory.")
