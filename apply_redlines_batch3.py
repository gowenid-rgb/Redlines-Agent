import fitz
import os
import shutil

# Directories
workspace_dir = r"C:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# List of drawings to process in this batch
drawings = [
    "93-020130 REV A.pdf",
    "93-023490 REV A.pdf",
    "93-023500 REV A.pdf",
    "93-023580 REV A.pdf"
]

# Backup files first if not already backed up
for d in drawings:
    src_path = os.path.join(workspace_dir, d)
    dst_path = os.path.join(backup_dir, d)
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        print(f"Backing up {d} to {dst_path}...")
        shutil.copy2(src_path, dst_path)

def apply_assembly_note_change(filename):
    part_no = filename.split(" ")[0]
    print(f"Processing {part_no}...")
    
    src_pdf = os.path.join(backup_dir, filename)
    doc = fitz.open(src_pdf)
    page = doc[0]
    
    # Insert Reference Note
    note_text = "Subparts in parent assembly have changed, please refer to the CAD and update assembly drawing as needed"
    nx, ny = 100.0, 1200.0
    note_pt = fitz.Point(nx, ny)
    page.insert_text(note_pt, note_text, fontsize=12, fontname="hebo", color=(1, 0, 0))
    
    # Calculate note width and bounding box for the revision cloud
    note_w = fitz.get_text_length(note_text, fontname="hebo", fontsize=12)
    note_cloud_rect = fitz.Rect(nx - 10, ny - 14, nx + note_w + 10, ny + 4)
    
    # Add note revision cloud
    cloud = page.add_rect_annot(note_cloud_rect)
    cloud.set_border(width=1.5, clouds=2)
    cloud.set_colors(stroke=(1, 0, 0))
    cloud.update()
    
    # Save the modified document
    out_pdf = os.path.join(workspace_dir, f"{part_no} redlines.pdf")
    doc.save(out_pdf)
    doc.close()
    
    # Render verification crops
    doc_ver = fitz.open(out_pdf)
    page_ver = doc_ver[0]
    
    # Crop 1: Note area
    crop_note_area = fitz.Rect(nx - 30, ny - 30, nx + note_w + 30, ny + 20)
    # Ensure crop area is within bounds
    crop_note_area = crop_note_area & page_ver.rect
    pix1 = page_ver.get_pixmap(clip=crop_note_area, matrix=fitz.Matrix(2, 2))
    crop_file1 = os.path.join(crops_dir, f"{part_no}_ref_note.png")
    pix1.save(crop_file1)
    print(f"  Saved verification crop (note): {crop_file1}")
    
    # Crop 2: Title block revision letter (x: 2360-2400, y: 1470-1530)
    crop_rev_area = fitz.Rect(2360, 1470, 2400, 1530)
    pix_rev = page_ver.get_pixmap(clip=crop_rev_area, matrix=fitz.Matrix(2, 2))
    rev_file = os.path.join(crops_dir, f"{part_no}_rev_letter.png")
    pix_rev.save(rev_file)
    print(f"  Saved verification crop (rev): {rev_file}")
    
    doc_ver.close()

# Process each drawing
for d in drawings:
    apply_assembly_note_change(d)

# Remove original clean files from main workspace
for d in drawings:
    original_path = os.path.join(workspace_dir, d)
    if os.path.exists(original_path):
        print(f"Removing original file from workspace: {d}")
        os.remove(original_path)

print("\nRedlining complete! Visual crop validation images generated in 'crops' directory.")
