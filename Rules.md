# PDF Drawing Redline Workflow & Rules

This document outlines the workflow, formatting rules, and technical process for automatically adding redline annotations and specification updates to PDF drawings.

---

## 1. Directory Structure

- **Workspace Folder (`\`)**: Contains the active drawings to process (e.g. `93-020131 REV A.pdf`).
- **Backup Folder (`\backup\`)**: Holds a copy of the clean, unmodified original drawings.
- **Output Naming**: The processed drawings are saved as `[part_number] redlines.pdf` (e.g., `93-020131 redlines.pdf`), and the original `REV A` source files are cleared from the main workspace.

---

## 2. Redlining & Formatting Rules

All markup is drawn in **Red** (`color = (1, 0, 0)`) to distinguish changes clearly:

### Specification Blocks (Material Changes)
- **Cell Layout**: The spec cell (bottom right quadrant, `x > 1700, y > 1300`) contains a small header label `SPECIFICATION` at the top left.
- **Old Value**: Crossed out with a horizontal red line.
- **New Value**: Placed in the upper-right area of the cell (baseline coordinates `x = 1860.0`, `y = 1374.0`) with a smaller font (`fontsize = 9, fontname = "hebo"` / Helvetica Bold). This prevents the new text from overlapping the `SPECIFICATION` header label.
- **Revision Cloud**: A rectangular annotation with a wavy cloud border (`clouds = 2`, `width = 1.5`) surrounds both the crossed-out value and the new value.

### Dimensions (Dimensional Changes)
- **Old Value**: Crossed out with a horizontal red line.
- **New Value**: Written in red bold (`fontsize = 14`, `fontname = "hebo"`) directly above the old value (shifted `8 points` upwards).
- **Revision Cloud**: A rectangular annotation with a wavy cloud border (`clouds = 2`, `width = 1.5`) surrounds both the crossed-out and the new dimension values.

### Revision History & Title Blocks
- **Revision History Block (Table)**: Left completely empty and unmodified.
- **Title Block Revision Letter**: Left exactly as-is (e.g., remains `A` with no markings). The support engineering team will determine major or minor revisions.

---

## 3. Automation Process (Python & PyMuPDF)

The automation script uses the `pymupdf` (fitz) library. Below is the layout of the processing script:

```python
import fitz
import os
import shutil

workspace_dir = r"."
filename = "93-020131 REV A.pdf"
part_no = filename.split(" ")[0]

doc = fitz.open(os.path.join(workspace_dir, filename))
page = doc[0]

# --- 1. Modify Specification ---
spec_rect = page.search_for("DENSITY")[0] # Filter for x > 1700, y > 1300

# Cross out
shape = page.new_shape()
shape.draw_line(fitz.Point(spec_rect.x0 - 5, spec_rect.y_mid), fitz.Point(spec_rect.x1 + 5, spec_rect.y_mid))
shape.finish(color=(1, 0, 0), width=1.5)
shape.commit()

# Write new spec
page.insert_text(fitz.Point(1860.0, 1374.0), "DENSITY: 1.8 lb/ft³, IFD: 36CA", fontsize=9, fontname="hebo", color=(1, 0, 0))

# Add cloud
cloud = page.add_rect_annot(fitz.Rect(spec_rect.x0 - 15, 1352.0, spec_rect.x1 + 15, spec_rect.y1 + 10))
cloud.set_border(width=1.5, clouds=2)
cloud.set_colors(stroke=(1, 0, 0))
cloud.update()

# --- 2. Save and Clean up ---
doc.save(os.path.join(workspace_dir, f"{part_no} redlines.pdf"))
doc.close()
os.remove(os.path.join(workspace_dir, filename))
```

---

## 4. Verification Check

Before final approval, visual crops are rendered for:
1. The **Specification block** (`x: 1700-2100`, `y: 1350-1430`) to verify alignment.
2. The **Dimension change block** (if applicable) to verify cloud bounds.
3. The **Title Block Revision letter** to confirm it remains unchanged.
