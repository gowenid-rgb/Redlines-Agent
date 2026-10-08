import fitz
import os
import shutil

# Directories
workspace_dir = r"C:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# Clean out old verification crops inside crops folder
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
    "93-020131 REV A.pdf",
    "93-023491 REV A.pdf",
    "93-023501 REV A.pdf",
    "93-023581 REV A.pdf"
]

# Backup files first if not already backed up
for d in drawings:
    src_path = os.path.join(workspace_dir, d)
    dst_path = os.path.join(backup_dir, d)
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        print(f"Backing up {d} to {dst_path}...")
        shutil.copy2(src_path, dst_path)

# Reference note coordinates on page 0 top surface
note_coords = {
    "93-020131": (730.0, 700.0),
    "93-023491": (810.0, 660.0),
    "93-023501": (830.0, 680.0),
    "93-023581": (860.0, 690.0)
}

def apply_spec_and_note_change(filename):
    part_no = filename.split(" ")[0]
    print(f"Processing {part_no}...")
    
    src_pdf = os.path.join(backup_dir, filename)
    doc = fitz.open(src_pdf)
    page = doc[0]
    
    # 1. Search for DENSITY in bottom right spec block (x > 1700, y > 1300)
    rects = page.search_for("DENSITY")
    spec_rect = None
    for r in rects:
        if r.x0 > 1700 and r.y0 > 1300:
            spec_rect = r
            break
            
    if not spec_rect:
        raise ValueError(f"Could not find DENSITY spec cell on page for {filename}")
        
    y_mid = (spec_rect.y0 + spec_rect.y1) / 2.0
    
    # 2. Cross out old density text
    shape = page.new_shape()
    shape.draw_line(fitz.Point(spec_rect.x0 - 5, y_mid), fitz.Point(spec_rect.x1 + 5, y_mid))
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    
    # 3. Write new specification
    new_spec = "DENSITY: 1.8 lb/ft³, IFD: 36CA"
    page.insert_text(fitz.Point(1860.0, 1374.0), new_spec, fontsize=9, fontname="hebo", color=(1, 0, 0))
    
    # 4. Add spec revision cloud
    spec_cloud_rect = fitz.Rect(spec_rect.x0 - 15, 1352.0, spec_rect.x1 + 15, spec_rect.y1 + 10)
    cloud1 = page.add_rect_annot(spec_cloud_rect)
    cloud1.set_border(width=1.5, clouds=2)
    cloud1.set_colors(stroke=(1, 0, 0))
    cloud1.update()
    
    # 5. Insert Reference Note "THRU SLOTS ADDED TO FACE" on Top Surface
    note_text = "THRU SLOTS ADDED TO FACE"
    nx, ny = note_coords[part_no]
    note_pt = fitz.Point(nx, ny)
    page.insert_text(note_pt, note_text, fontsize=12, fontname="hebo", color=(1, 0, 0))
    
    # 6. Add note revision cloud
    # Text length in fontsize 12 is about 185 points. Bounding box calculation:
    note_w = fitz.get_text_length(note_text, fontname="hebo", fontsize=12)
    note_cloud_rect = fitz.Rect(nx - 10, ny - 14, nx + note_w + 10, ny + 4)
    cloud2 = page.add_rect_annot(note_cloud_rect)
    cloud2.set_border(width=1.5, clouds=2)
    cloud2.set_colors(stroke=(1, 0, 0))
    cloud2.update()
    
    # Save the modified document
    out_pdf = os.path.join(workspace_dir, f"{part_no} redlines.pdf")
    doc.save(out_pdf)
    doc.close()
    
    # Render verification crops
    doc_ver = fitz.open(out_pdf)
    page_ver = doc_ver[0]
    
    # Crop 1: Spec block
    pix1 = page_ver.get_pixmap(clip=fitz.Rect(1700, 1340, 2100, 1425), matrix=fitz.Matrix(2, 2))
    crop_file1 = os.path.join(crops_dir, f"{part_no}_spec_block.png")
    pix1.save(crop_file1)
    print(f"  Saved verification crop (spec): {crop_file1}")
    
    # Crop 2: Note
    crop_note_area = fitz.Rect(nx - 30, ny - 30, nx + note_w + 30, ny + 20)
    pix2 = page_ver.get_pixmap(clip=crop_note_area, matrix=fitz.Matrix(2, 2))
    crop_file2 = os.path.join(crops_dir, f"{part_no}_ref_note.png")
    pix2.save(crop_file2)
    print(f"  Saved verification crop (note): {crop_file2}")
    
    # Crop 3: Title block revision letter (x: 2360-2400, y: 1470-1530)
    pix_rev = page_ver.get_pixmap(clip=fitz.Rect(2360, 1470, 2400, 1530), matrix=fitz.Matrix(2, 2))
    rev_file = os.path.join(crops_dir, f"{part_no}_rev_letter.png")
    pix_rev.save(rev_file)
    print(f"  Saved verification crop (rev): {rev_file}")
    
    doc_ver.close()

# Process each drawing
for d in drawings:
    apply_spec_and_note_change(d)

# Remove original clean files from main workspace
for d in drawings:
    original_path = os.path.join(workspace_dir, d)
    if os.path.exists(original_path):
        print(f"Removing original file from workspace: {d}")
        os.remove(original_path)

print("\nRedlining complete! Visual crop validation images generated in 'crops' directory.")
