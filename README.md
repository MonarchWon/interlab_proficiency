# Youden Plot Inter-Laboratory Generator

This repository contains an advanced diagnostic graphics suite for Proficiency Testing (QA/QC), built for identical blind-duplicate testing. It evaluates systemic calibration bias versus random measurement error across participating laboratories by rendering geometric 95% Confidence Ellipses mapped to the group consensus Medians.

The project offers two independent tools: a **Web Dashboard** and a **Python Batch Processor**.

---

## 1. Using the Web Dashboard

The `index.html` file runs entirely inside your local web browser. Simply double-click `index.html` to open it in Chrome, Edge, or Safari.

- **Upload Data:** Use the "Upload Excel" button to natively inject your data from `.xlsx` files.
- **Toggles:** Select your targeted worksheets using the Worksheet dropdown.
- **Robust Math Mode:** Click the "Using: Standard Bounds / Robust Bounds" button at the top to toggle purely between geometric (Mean-centric) variance and heavily constrained Robust Statistics (Median Absolute Deviation).
- **Outliers:** Deselect any laboratory from the left sidebar to instantly remove them from the math and watch the confidence geometry recalculate in real-time.

---

## 2. Using the Python Batch Processor

The Python version (`youden_plot.py`) is designed for heavy lifting. Instead of clicking through a web page, you can drop fifty Excel spreadsheets into a folder and perfectly stamp out fifty high-resolution `.png` graphs in seconds.

### **Initial Setup (One Time)**
Ensure you have Python installed, then install the scientific dependencies:
```cmd
pip install -r requirements.txt
```

### **How to generate plots:**
1. Navigate to the project folder (`youden_plot`).
2. Inside that folder, you will see a folder named `data`. Place any `.xlsx` or `.xls` Excel spreadsheets you wish to analyze directly into this `data` folder.
   *(Note: The excel data must begin on Row 2, structured as `[Lab ID] | [Sample 1 Result] | [Sample 2 Result]`)*.
3. Once your files are dropped into `data\`, simply run the generator script via your terminal/command prompt:
```cmd
python youden_plot.py
```
*(If `python` isn't mapped, try `python3 youden_plot.py` or `py youden_plot.py`)*

### **What Happens Next?**
The script will silently rip through every single Excel file and worksheet inside `data\`. For every worksheet it parses, it will automatically generate and save a high-resolution, static `youden_WORKSHEETNAME.png` image directly alongside the spreadsheet! It uses custom label-collision physics (`adjustText`) to cleanly untangle overlapping laboratory tags.

### **Excluding Labs in Python:**
If you need to discard known corrupted labs before calculating the geometry, open `youden_plot.py` in a text editor and search for:
`LABS_TO_EXCLUDE = []`
Add your lab strings (e.g. `LABS_TO_EXCLUDE = ["Lab24", "Lab10"]`) to completely ignore them.
