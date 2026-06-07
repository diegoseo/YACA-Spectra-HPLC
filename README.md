<div align="center">

<img src="assets/logo_yacaspectra2.png" alt="YACA-Spectra logo" width="180"/>

# YACA-Spectra HPLC Educational

### Educational desktop software for HPLC/QGD chromatogram visualization, ROI selection, peak integration, centroid calculation, and chromatographic signal comparison.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Status-Educational-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

[Español](README.es.md)

</div>

---

## Overview

**YACA-Spectra HPLC Educational** is a Python desktop application designed for educational activities in chromatographic signal analysis.

The software allows users to load `.qgd` chromatographic files, visualize TIC-like chromatograms, select regions of interest, integrate peaks, calculate centroid and apex values, estimate peak area percentages, and compare multiple chromatographic signals.

---

## Main features

| Module            | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| Data loading      | Open chromatographic `.qgd` files                                    |
| Visualization     | Display chromatograms as intensity vs. retention time                |
| ROI selection     | Select peak regions using two mouse clicks                           |
| Peak integration  | Calculate area, centroid, apex retention time, and maximum intensity |
| Processing        | Apply moving-average smoothing and linear baseline correction        |
| Export            | Export chromatographic data and ROI tables as CSV files              |
| Signal comparison | Compare multiple chromatographic signals in a dedicated window       |
| Language support  | Interface available in English and Spanish                           |

---

## Project structure

```text
YACA_SPECTRA/
├── assets/
│   └── logo_yacaspectra2.png
├── docs/
│   └── screenshots/
│       ├── 01_main_window_es.png
│       ├── 02_open_qgd_es.png
│       ├── 03_loaded_chromatogram_es.png
│       ├── 04_roi_selection_es.png
│       ├── 05_integrated_roi_es.png
│       ├── 06_compare_window_es.png
│       └── 07_language_selector_es.png
├── docs-en/
│   └── screenshots/
│       ├── 01_main_window_en.png
│       ├── 02_open_qgd_en.png
│       ├── 03_loaded_chromatogram_en.png
│       ├── 04_roi_selection_en.png
│       ├── 05_integrated_roi_en.png
│       ├── 06_compare_window_en.png
│       └── 07_language_selector_en.png
├── sample_data/
│   └── BFC 267 (2).qgd
├── yaca_spectra.py
├── translations.py
├── requirements.txt
├── README.md
├── README.es.md
├── USER_MANUAL.md
├── Manual_Usuario.md
├── LICENSE
├── YACA-Spectra-HPLC-Linux.spec
└── .gitignore
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/diegoseo/YACA-Spectra-HPLC.git
cd YACA-Spectra-HPLC
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the application

```bash
python yaca_spectra.py
```

---

## Dependencies

The main dependencies are:

```text
numpy
pandas
matplotlib
pillow
olefile
```

All required packages are listed in `requirements.txt`.

---

## Basic workflow

1. Open the application.
2. Click **Open QGD**.
3. Select a chromatographic `.qgd` file.
4. Visualize the chromatogram.
5. Select a region of interest using two clicks.
6. Integrate the selected peak.
7. Export the chromatogram, export ROI results, or compare multiple signals.

---

## Example data

Example files may be included in:

```text
sample_data/
```

If `.qgd` files contain private or laboratory data, they should not be uploaded to a public repository.

---

## Notes

* This software uses **Tkinter**, so it must be executed in an environment with a graphical interface.
* On Linux, if a Tkinter-related error appears, install Tk support:

```bash
sudo apt install python3-tk
```

* If logo images are not available, the program can still run using text placeholders.
* The expected input files are chromatograms with the `.qgd` extension.

---

## Educational purpose

YACA-Spectra HPLC Educational was designed to support the teaching of chromatographic concepts such as:

* Retention time.
* Peak identification.
* Region of interest selection.
* Chromatographic peak integration.
* Relative peak area.
* Centroid and apex calculation.
* Baseline correction.
* Signal smoothing.
* Comparison of chromatographic profiles.

---

## Downloads

Executable versions are available in the [Releases](../../releases) section.

### Latest release files

| Operating system | File                             |
| ---------------- | -------------------------------- |
| Linux            | `YACA-Spectra-HPLC-Linux.tar.gz` |
| Windows          | `YACA-Spectra-HPLC-Windows.exe`  |
| macOS            | `YACA-Spectra-HPLC-macOS.zip`    |

### Running on Linux

Download `YACA-Spectra-HPLC-Linux.tar.gz`, extract it, give execution permission, and run the application:

```bash
tar -xzf YACA-Spectra-HPLC-Linux.tar.gz
chmod +x YACA-Spectra-HPLC-Linux
./YACA-Spectra-HPLC-Linux
```

### Running on Windows

Download and run:

```text
YACA-Spectra-HPLC-Windows.exe
```

If Windows shows a security warning, choose **More info → Run anyway** only if you downloaded the file from the official release page.

### Running on macOS

Download and extract:

```text
YACA-Spectra-HPLC-macOS.zip
```

Then open the `.app` file. If macOS shows a security warning because the application is not signed or notarized, use **Right click → Open**.


---

## License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

---

<div align="center">

**YACA-Spectra HPLC Educational**
Educational chromatographic signal analysis software.

</div>
