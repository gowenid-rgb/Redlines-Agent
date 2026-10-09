# PDF Drawing Redline Workflow & Rules

This document outlines the workflow, formatting rules, PDF layout conventions, and technical process for automatically adding redline annotations and specification updates to engineering drawings.

---

## 1. Drawing Format & Layout Zones

Our engineering drawings follow a standard ANSI D/E format (`2448 x 1584 pt` unscaled):

| Zone | Coordinates (PDF Points) | Contents | Redline Rules |
| :--- | :--- | :--- | :--- |
| **Title Block (Bottom Right)** | `x: 1700 - 2400`, `y: 1250 - 1550` | `SPECIFICATION` (Density & IFD), `MATERIAL`, Drawing Number, Part Name, Rev Letter | Old specs/materials crossed out with horizontal line; new text written directly in red bold with revision cloud. **Rev Letter remains UNTOUCHED**. |
| **Drawing Window (Center)** | `x: 200 - 1700`, `y: 200 - 1200` | Front View, Side View, Isometric Views, Dimension lines, Callouts | Old dimensions crossed out with horizontal line; new dual-unit dimensions written directly above with revision cloud. |
| **Open Drawing Area (Top Center)** | `x: 800 - 1400`, `y: 100 - 250` | Open space above drawing views | Placement for prominent engineering text notes (e.g. Dacron fiber wrap seam position) with large font (>= 24 pt) and revision cloud. |
| **Revision History (Top Right)** | `x: 1500 - 2400`, `y: 50 - 180` | ECO#, Zone, Description, Date, Drawn, Approved | Revision bumps & change logs are recorded here. Left empty during preliminary markup. |
| **General Notes (Bottom Left)** | `x: 50 - 1200`, `y: 1250 - 1500` | Numbered standard notes 1 to 9 | Standard general manufacturing notes. |

---

## 2. Dimension Identification & Dual Units Standard

### Identifying Dimensions
- **Thickness**: Usually the **smallest linear dimension** on the drawing, located on the side view profile (e.g., `101.60 mm = 4.00 in`). Chamfer cutouts/angles (e.g. `2X 38.1 X 30°` containing `X` or `°`) are excluded.
- **Width & Length**: The primary outer dimensions on the front view (e.g., `812.8 mm` / `825.5 mm` = ~32.0" to 32.5").
- **Specific Callouts**: When users specify dimensions (e.g. "change from 841mm to 956" or "change 825.5 to 831.9"), search for that numeric value directly on the drawing.

### Dual Dimensioning Requirement
All dimension redlines must list **both inches and millimeters**:
- If specified in inches: format as `{inches}" ({mm} mm)`, e.g., `4.5" (114.3 mm)` or `32.75" (831.9 mm)`.
- If specified in millimeters: format as `{inches}" ({mm} mm)`, e.g., `37.64" (956.0 mm)`.

---

## 3. Redlining & Formatting Rules

All markup is drawn in **Red** (`#FF0000` / RGB `1.0, 0.0, 0.0`):

### Specification Blocks & Material Changes (Title Block Rule)
- **CRITICAL - NO TITLE BLOCK OVERLAPPING**: Notes must NEVER be drawn directly inside the title block grid cells, as red text overlaps black title block text and grid lines, making it illegible.
- **Placement**: The revision note must be posted **above the title block** in the clear open drawing area (`x: ~1680, y: ~1060`), formatted with prominent red bold text and enclosed in a revision cloud.
- **Leader Line & Arrow**: Draw a red leader line (with a smooth curve or dogleg) and filled arrowhead pointing down from the revision note into the specific title block cell where the spec or material changed.
- **Strike-Through**: The old value inside the title block cell (e.g. `DENSITY: 2.5 lb/ft³, IFD: 28 HR` or `POLYURETHANE FOAM`) is cleanly struck through with a red horizontal line.

### Dimensions
- **Old Value**: Crossed out with a horizontal red line.
- **New Value**: Written in red bold (font size >= 20 pt, typically 24 pt) directly above the old value in dual units.
- **Revision Cloud**: Wavy revision cloud surrounds both old and new dimension values.

### Zero-Ghosting Policy
- **Strictly User-Requested Changes Only**: Redlines must ONLY be created for items explicitly requested in the user prompt.
- **No Unprompted Injections**: NEVER generate a 32.75" dimension change or a seam position note unless the user explicitly requested it in their input.

### Title Block Revision Letter Protection
- **Title Block Revision Letter**: Must be left completely untouched. The support engineering team classifies major vs. minor revisions.

---

## 4. Automation Process (Python & Client Engine)

1. **Extract Text Elements**: Use vector text inspection (`page.get_text('words')` in PyMuPDF or `page.getTextContent()` in PDF.js) to find exact bounding box coordinates of all text and dimensions.
2. **Locate Target Elements**:
   - Thickness -> locate smallest linear dimension on side view.
   - Specs -> locate `DENSITY` / `IFD` / `SPECIFICATION` in bottom-right title block.
   - Materials -> locate `MATERIAL` in bottom-right title block.
3. **Apply Markup**: Strike through old text at its exact coordinates, insert dual-unit text above, and wrap in a wavy revision cloud.

---

## 5. Batch Redlining & Multi-Drawing Intelligence

### Multi-Drawing Ingestion & Universal Prompts
- Users can drop a batch of engineering PDF drawings at once into the drop zone.
- Prompts are interpreted globally across the entire batch rather than just for the actively viewed drawing.
- The AI / rule engine detects which changes apply universally (e.g., all cushions changing to `31"x31"x4.5"`) and which apply conditionally based on drawing properties.

### Firmness Identifier & Specification Mapping
Engineering cushion drawings are automatically classified into firmness tiers based on their title block and drawing text:
- **SOFT**: Identified by `SOFT` in the drawing title or existing title block IFD `24`.
  - Maps to user-specified Soft specs (e.g., `1.9/30` -> `DENSITY: 1.9 lb/ft³, IFD: 30`).
- **MEDIUM**: Identified by `MEDIUM` in the drawing title or existing title block IFD `28`.
  - Maps to user-specified Medium specs (e.g., `2.0/31` -> `DENSITY: 2.0 lb/ft³, IFD: 31`).
- **FIRM**: Identified by `FIRM` in the drawing title or existing title block IFD `42` / `35`.
  - Maps to user-specified Firm specs (e.g., `2.5/35` -> `DENSITY: 2.5 lb/ft³, IFD: 35`).

### 3D Bounding Dimensions in Batch Processing
When a bounding dimension is requested (e.g., `31"x31"x4.5"`):
- The planar width and length (larger dimensions, e.g., `31" / 787.4 mm`) are redlined on the front view of all cushions in the batch.
- The thickness (smallest dimension, e.g., `4.5" / 114.3 mm`) is redlined on the side view profile across all cushions in the batch.

### Batch Review & Export
- The user can click any drawing in the batch list to visually inspect the applied redlines in the Output Window.
- **Single PDF Download**: Click "Download PDF" to export the active drawing with high-fidelity vector redlines.
- **Batch ZIP Download**: Click "Download All (ZIP)" to bundle all redlined drawings into a single organized ZIP archive (`Batch_Redlines_YYYY-MM-DD.zip`).

