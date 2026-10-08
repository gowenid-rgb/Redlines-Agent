# Redlines-Agent

Automated CAD Drawing Redline Studio & Engineering Change Assistant.

## Features
- **Standalone HTML Redline Tool (`redline_tool.html`)**:
  - Drag and drop multi-drawing input (PDF, DWG, images)
  - Context & instruction window with one-click presets
  - Interactive PDF canvas viewer with zoom, pan, and page navigation
  - Vector redline markup (strike-throughs, bold text, wavy revision clouds)
  - Re-prompt iteration bar for quick follow-up adjustments
  - Downloadable redline drawings (`[part_number] redlines.pdf`) via `pdf-lib`
  - Integrated `Rules.md` specifications
  - Google Gemini API integration (Gemini 2.5/1.5 Flash/Pro) + Offline simulation mode
- **Engineering Drawing Rules (`Rules.md`)**:
  - Font size $\ge 24\text{ pt}$ for notes and major callouts
  - Red `#FF0000` markup with wavy revision clouds
  - Unmodified revision history blocks and protected title block revision letters
- **Python Automation**:
  - PyMuPDF scripts for automated batch processing and crop verification

## Deployment (Railway / Cloud)
- **Direct Web Access**: Serves `index.html` via `server.py` on `$PORT`.
- **Dockerfile & Procfile**: Included for instant one-click deployment on platforms like Railway.
