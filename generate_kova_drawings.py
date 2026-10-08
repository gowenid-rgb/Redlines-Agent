import fitz
import os
import shutil

workspace_dir = r"c:\Users\gowen\OneDrive - Exemplis\Desktop\Coding Tools\Redlines"
kova_dir = os.path.join(workspace_dir, "Kova 3.5 - Flange Pillow Order - 7.21")
backup_dir = os.path.join(workspace_dir, "backup")
crops_dir = os.path.join(workspace_dir, "crops")

os.makedirs(backup_dir, exist_ok=True)
os.makedirs(crops_dir, exist_ok=True)

# Templates
template_45_name = "93-027268.pdf"
template_70_name = "93-027268  -70 deg template.PDF"

template_45_src = os.path.join(kova_dir, template_45_name)
template_70_src = os.path.join(kova_dir, template_70_name)

backup_45_path = os.path.join(backup_dir, template_45_name)
backup_70_path = os.path.join(backup_dir, template_70_name)

if os.path.exists(template_45_src) and not os.path.exists(backup_45_path):
    print(f"Backing up {template_45_name} to {backup_45_path}...")
    shutil.copy2(template_45_src, backup_45_path)

if os.path.exists(template_70_src) and not os.path.exists(backup_70_path):
    print(f"Backing up {template_70_name} to {backup_70_path}...")
    shutil.copy2(template_70_src, backup_70_path)

drawings_data = [
    {
        "part_no": "93-027268",
        "size_str": "30X30",
        "dim_in": "30.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 2.5 Density: 24 HR",
        "material_str": "Polyurethane foam",
        "template_path": backup_45_path
    },
    {
        "part_no": "93-027269",
        "size_str": "31X31",
        "dim_in": "31.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 2.5 Density: 24 HR",
        "material_str": "Polyurethane foam",
        "template_path": backup_45_path
    },
    {
        "part_no": "93-027270",
        "size_str": "32X32",
        "dim_in": "32.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 2.5 Density: 24 HR",
        "material_str": "Polyurethane foam",
        "template_path": backup_45_path
    },
    {
        "part_no": "93-027271",
        "size_str": "32X32",
        "dim_in": "32.0in",
        "thickness_in": "4.0in",
        "angle_str": "70°",
        "spec_str": "IFD: 2.5 Density: 24 HR",
        "material_str": "Polyurethane foam",
        "template_path": backup_70_path
    },
    {
        "part_no": "93-027272",
        "size_str": "31X31",
        "dim_in": "31.0in",
        "thickness_in": "4.0in",
        "angle_str": "70°",
        "spec_str": "IFD: 2.5 Density: 24 HR",
        "material_str": "Polyurethane foam",
        "template_path": backup_70_path
    },
    # 3 New Drawings
    {
        "part_no": "93-027273",
        "size_str": "32X32",
        "dim_in": "32.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 24 Density: 1.8",
        "material_str": "Conventional foam",
        "template_path": backup_45_path
    },
    {
        "part_no": "93-027274",
        "size_str": "32X32",
        "dim_in": "32.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 24 Density: 2.5",
        "material_str": "HR foam",
        "template_path": backup_45_path
    },
    {
        "part_no": "93-027275",
        "size_str": "32X32",
        "dim_in": "32.0in",
        "thickness_in": "4.0in",
        "angle_str": "45°",
        "spec_str": "IFD: 30 Density: 2.5",
        "material_str": "HR foam",
        "template_path": backup_45_path
    }
]

def replace_text_in_rect(page, rect, new_text, fontsize=16, fontname="hebo", color=(0,0,0)):
    page.add_redact_annot(rect, fill=(1,1,1))
    page.apply_redactions()
    pt = fitz.Point(rect.x0, rect.y1 - 2)
    page.insert_text(pt, new_text, fontsize=fontsize, fontname=fontname, color=color)

def generate_drawing(item):
    part_no = item["part_no"]
    dim_val = item["dim_in"]
    thick_val = item["thickness_in"]
    angle_val = item["angle_str"]
    size_str = item["size_str"]
    spec_val = item["spec_str"]
    mat_val = item["material_str"]
    tmpl_path = item["template_path"]

    print(f"\nGenerating drawing for {part_no} ({size_str} @ {angle_val}, template: {os.path.basename(tmpl_path)})...")
    doc = fitz.open(tmpl_path)

    for p_idx, page in enumerate(doc):
        # 1. Update Title Block DWG NO.
        dwg_rects = page.search_for("DWG.  NO.")
        if dwg_rects:
            r = dwg_rects[0]
            pt_dwg = fitz.Point(r.x0 + 65, r.y1 - 2)
            page.insert_text(pt_dwg, part_no, fontsize=14, fontname="hebo", color=(0,0,0))

        # 2. Update Title Block Title
        title_rects = page.search_for("TITLE")
        if title_rects:
            r = title_rects[0]
            line1 = f"FOAM, {size_str} FLANGE PILLOW"
            line2 = "KOVA 3.5"
            pt_t1 = fitz.Point(r.x0, r.y1 + 18)
            pt_t2 = fitz.Point(r.x0, r.y1 + 36)
            page.insert_text(pt_t1, line1, fontsize=13, fontname="hebo", color=(0,0,0))
            page.insert_text(pt_t2, line2, fontsize=13, fontname="hebo", color=(0,0,0))

        # 3. Update Specification Block
        spec_rects = page.search_for("SPECIFICATION")
        if spec_rects:
            r = spec_rects[0]
            pt_spec = fitz.Point(r.x0, r.y1 + 16)
            page.insert_text(pt_spec, spec_val, fontsize=10, fontname="hebo", color=(0,0,0))

        # 4. Update Material Block in Title Block (x > 1700, y > 1250)
        mat_rects = page.search_for("MATERIAL")
        for r in mat_rects:
            if r.x0 > 1700 and r.y0 > 1250:
                pt_mat = fitz.Point(r.x0, r.y1 + 16)
                page.insert_text(pt_mat, mat_val, fontsize=10, fontname="hebo", color=(0,0,0))
                break

        # 5. Page 1 specific dimension, thickness, & angle replacements
        if p_idx == 0:
            # Search for 'Dim' or 'dim' placeholders for Top & Mid dimensions
            # Top Dim (x ~ 467..472, y ~ 213)
            for term in ["Dim", "dim"]:
                rects = page.search_for(term)
                for r in rects:
                    if abs(r.x0 - 470) < 30 and abs(r.y0 - 213) < 30:
                        replace_text_in_rect(page, r, dim_val, fontsize=16, fontname="hebo")

            # Mid Dim (x ~ 704..708, y ~ 450)
            for term in ["Dim", "dim"]:
                rects = page.search_for(term)
                for r in rects:
                    if abs(r.x0 - 706) < 30 and abs(r.y0 - 450) < 30:
                        replace_text_in_rect(page, r, dim_val, fontsize=16, fontname="hebo")

            # Top & Bot Deg
            for term in ["Deg", "deg", "70"]:
                rects = page.search_for(term)
                for r in rects:
                    if (abs(r.x0 - 1408) < 50 or abs(r.x0 - 1559) < 50) and abs(r.y0 - 580) < 30:
                        replace_text_in_rect(page, r, angle_val, fontsize=16, fontname="hebo")
                    elif (abs(r.x0 - 1405) < 50 or abs(r.x0 - 1542) < 50) and (abs(r.y0 - 1108) < 40 or abs(r.y0 - 1076) < 40):
                        replace_text_in_rect(page, r, angle_val, fontsize=16, fontname="hebo")

            # Detail E thickness (dim at x ~ 1670..1792, y ~ 817..838)
            for term in ["dim", "Dim"]:
                rects = page.search_for(term)
                for r in rects:
                    if (abs(r.x0 - 1670.5) < 40 or abs(r.x0 - 1792.8) < 40) and abs(r.y0 - 830) < 40:
                        replace_text_in_rect(page, r, thick_val, fontsize=16, fontname="hebo")

    out_file = os.path.join(kova_dir, f"{part_no}.pdf")
    doc.save(out_file)
    doc.close()
    print(f"Saved {out_file}")

    # Generate verification crops
    doc_ver = fitz.open(out_file)
    p0 = doc_ver[0]

    # Title block crop (with Material & Spec)
    pix_tb = p0.get_pixmap(clip=fitz.Rect(1750, 1280, 2410, 1550), dpi=150)
    pix_tb.save(os.path.join(crops_dir, f"{part_no}_title_block.png"))

    # Dimension crop Page 1
    pix_dim = p0.get_pixmap(clip=fitz.Rect(400, 150, 1850, 1150), dpi=100)
    pix_dim.save(os.path.join(crops_dir, f"{part_no}_drawing_dims.png"))

    doc_ver.close()
    print(f"Generated verification crops for {part_no}")

for d in drawings_data:
    generate_drawing(d)

print("\nAll drawings successfully updated!")
