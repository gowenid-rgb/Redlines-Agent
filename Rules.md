# Universal PDF Drawing Redline Workflow & Rules

This document outlines the workflow, formatting rules, PDF layout conventions, and autonomous intelligence for adding redline annotations and engineering changes to technical CAD drawings across any industry (aerospace, mechanical, architecture, woodworking, sheet metal, furniture, electronics, etc.).

---

## 1. Universal Drawing Layout & Zones

Engineering drawings across all disciplines follow standard CAD layout conventions (ANSI A-E, ISO A4-A0):

| Zone | Typical PDF Coordinates | Contents | Universal Redline Rules |
| :--- | :--- | :--- | :--- |
| **Title Block** | Bottom-Right Quadrant or Bottom Band | Part Name / Title, Part Number, Material, Finish, Specification, Tolerances, Rev Letter | Old values cleanly struck through with a red horizontal line. Replacement notes posted **ABOVE or ADJACENT** to the title block with a curved leader arrow pointing to the struck-through cell. **Rev letter is left untouched**. |
| **Drawing Views Area** | Main Center Window (`x: 10% - 80%`, `y: 10% - 80%`) | Orthographic views (Front, Top, Side, Section, Isometric), Dimensions, Callouts | Old dimensions struck through; new values written directly above in bold red with dual units, enclosed in a wavy revision cloud. |
| **Clear Drawing Area** | Open Space (e.g. Top Center or Left) | Notes, General Requirements | General engineering notes (e.g., deburring, treatment, seam positions, tolerances) drawn with large text (>= 24 pt) and revision cloud. |
| **Revision History Table** | Top-Right or Top-Left Corner | Revision letters, ECO #, change descriptions, approvals | Controlled by document management systems. Left untouched during preliminary markup. |

---

## 2. Universal Dimension Identification & Dual Units

### Identifying Drawing Dimensions
The system automatically extracts all numeric dimensions, fractions, and callouts (diameters `Ø`, radii `R`, chamfers, thread pitches, angles `°`):
- **Thickness / Depth**: The smallest profile dimension on side/section views.
- **Length / Width / Profile**: The primary outer envelope dimensions on main orthographic views.
- **Specific Callouts**: When users specify dimensions (e.g. "change 825.5 to 831.9" or "change 1/2-inch bore to 5/8-inch"), the system matches that numeric value and text directly on the sheet.

### Dual Dimensioning Standard
Engineering redlines standardly provide dual units (inches and millimeters) for global manufacturing clarity:
- Formatted as: `{inches}" ({mm} mm)` or `{primary} ({secondary})`.
- Example: `4.5" (114.3 mm)` or `31.00" (787.4 mm)`.

---

## 3. Redlining & Drafting Rules

All markup is drawn in **Pure Red** (`#FF0000` / RGB `1.0, 0.0, 0.0`):

### Title Block Protection & Leader Arrow Standard
- **CRITICAL - NO TITLE BLOCK OVERLAPPING**: Red text must NEVER be drawn inside the title block grid cells, as overlapping black text and border lines creates an illegible mess.
- **Placement**: Revision notes (`REVISED [PROPERTY]: [NEW VALUE]`) are posted in open space **above or adjacent to the title block** (`x: ~1680, y: ~1060`), enclosed in a revision cloud.
- **Leader Line & Arrow**: A curved red leader line with a filled arrowhead points directly from the revision cloud into the struck-through cell in the title block.
- **Strike-Through**: The existing value in the title block cell is cleanly struck through with a horizontal red line.

### Dimensions
- **Strike-Through**: Old dimension text is cleanly crossed out.
- **New Value**: Written in red bold font (size >= 20-24 pt) directly above the old value.
- **Revision Cloud**: Wavy revision cloud encloses both the struck-through dimension and the new value.

### Zero-Ghosting Policy
- **Strictly User-Requested Changes Only**: Redlines are ONLY created for elements explicitly requested in the user prompt.
- **No Unprompted Injections**: The agent never injects phantom notes, dimensions, or changes from previous runs.

### Title Block Revision Letter Protection
- The drawing revision letter block is preserved and never modified automatically.

---

## 4. Universal Multi-Drawing Batch Intelligence

### Domain-Agnostic Processing
Whether processing rocket engine components, wood cabinetry panels, sheet metal brackets, or upholstery cushions:
- Users drop any batch of CAD PDF drawings into the workspace.
- The prompt is evaluated against the entire batch simultaneously.

### Universal & Conditional Logic
The AI interprets natural language prompts and applies changes accordingly:
- **Universal Changes**: Changes that apply across all drawings in the batch (e.g., "Change overall dimensions to 31x31x4.5" or "Update material to 6061-T6 Aluminum on all parts").
- **Conditional / Variant Changes**: Changes that apply to specific subsets of drawings based on part properties, titles, materials, finishes, or part numbers (e.g., "For parts with 'SOFT', spec is 1.9/30; for 'FIRM', spec is 2.5/35", or "For Grade A panels, core is Baltic Birch").
- **Explicit Overrides**: Targeted modifications to specific parts or dimensions (e.g., "On part 100-241, change bore diameter to 14.3mm").

### Batch Review & 1-Click Export
- Users can click any drawing in the batch list to visually review the markup in the interactive Output Window.
- **Download PDF**: Exports the currently viewed drawing with full vector redlines.
- **Download All (ZIP)**: Generates and packages every redlined drawing in the batch into a single organized ZIP archive (`Batch_Redlines_YYYY-MM-DD.zip`).
