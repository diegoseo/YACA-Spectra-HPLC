<div align="center">

<img src="assets/logo_yacaspectra2.png" alt="YACA-Spectra logo" width="160"/>

# User Manual

## YACA-Spectra HPLC Educational

Educational software for HPLC/QGD chromatogram visualization, ROI selection, peak integration, centroid calculation, and chromatographic signal comparison.

[Versión en español](USER_MANUAL.md)

</div>

---

## 1. Introduction

**YACA-Spectra HPLC Educational** is a Python desktop application designed to support educational activities related to HPLC/QGD chromatographic signal analysis.

The software allows users to load `.qgd` chromatographic files, visualize chromatographic signals, select regions of interest, integrate peaks, calculate centroid, apex retention time, maximum intensity, peak area, and area percentage. It also allows the comparison of multiple chromatographic signals in a dedicated window.

---

## 2. System requirements

To run the program, the following requirements are needed:

* Python 3.12 or higher.
* Windows, Linux, or macOS.
* A graphical desktop environment.
* Dependencies installed from `requirements.txt`.

The main libraries used by the program are:

```text
numpy
pandas
matplotlib
pillow
olefile
```

On Linux, if a Tkinter-related error appears, install Tk support with:

```bash
sudo apt install python3-tk
```

---

## 3. Installation

### 3.1 Create a virtual environment

```bash
python -m venv .venv
```

### 3.2 Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 3.3 Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Running the program

Run the application with:

```bash
python yaca_spectra.py
```

After starting the program, the main window of YACA-Spectra HPLC Educational will open.

![Main window](docs-en/screenshots/01_main_window_es.png)

---

## 5. Main interface overview

The main interface is divided into five main regions:

1. **File loading and basic processing**
   Allows users to open `.qgd` files, apply smoothing, select baseline correction, export data, and open the signal comparison window.

2. **HPLC/QGD chromatogram**
   Displays the chromatographic signal as intensity versus retention time.

3. **ROI selection**
   Allows users to define a region of interest for peak integration.

4. **Educational summary**
   Displays the number of integrated ROIs, total area, and currently loaded file.

5. **Integrated regions**
   Shows a table with the results of each integrated ROI.

---

## 6. Loading a QGD file

To load a chromatographic file:

1. Click **Open QGD**.
2. Select a file with the `.qgd` extension.
3. Confirm the selection.

![Open QGD file](docs-en/screenshots/02_open_qgd_es.png)

After loading the file, the chromatogram will appear in the plot area.

![Loaded chromatogram](docs-en/screenshots/03_loaded_chromatogram_es.png)

---

## 7. Chromatogram visualization

The plot displays:

* X-axis: retention time, RT, in minutes.
* Y-axis: signal intensity.
* Chromatographic peaks associated with detected signals at different retention times.

The Matplotlib toolbar can be used to:

* Zoom into a region.
* Pan the plot.
* Return to the original view.
* Save the plot as an image.

---

## 8. Applying smoothing

The **Smoothing** field applies a simple moving-average filter to the chromatographic signal.

Steps:

1. Enter a value in the **Smoothing** field.
2. Click **Apply smoothing**.

Small values preserve the original peak shape better. Very high values may distort the signal or reduce the resolution between close peaks.

---

## 9. Baseline correction

The program allows the user to select the baseline correction mode:

* **none**: no baseline correction is applied.
* **linear**: subtracts a linear baseline between the beginning and end of the ROI.

Linear baseline correction can modify the calculated peak area, especially when the signal presents baseline drift or inclination.

---

## 10. Selecting an ROI

An ROI, or region of interest, is an interval of the chromatogram selected for peak analysis.

To create an ROI:

1. Click **Create ROI with 2 clicks**.
2. Click once before the peak.
3. Click again after the peak.

![ROI selection](docs-en/screenshots/04_roi_selection_es.png)

After selecting the region, the program automatically fills in:

* ROI start.
* ROI end.
* Centroid.
* Apex RT.
* Maximum intensity.

---

## 11. Integrating an ROI

To integrate an ROI:

1. Select a region of interest.
2. Click **Integrate ROI**.

The result will appear in the **Integrated regions** table.

![Integrated ROI](docs-en/screenshots/05_integrated_roi_es.png)

The table shows:

| Column   | Meaning                                                                     |
| -------- | --------------------------------------------------------------------------- |
| ROI      | Integrated region number                                                    |
| Start    | Initial retention time of the ROI                                           |
| End      | Final retention time of the ROI                                             |
| Centroid | Weighted center of the peak                                                 |
| Apex RT  | Retention time of the peak maximum                                          |
| Max. I   | Maximum peak intensity                                                      |
| Area     | Integrated peak area                                                        |
| % Area   | Relative contribution of that ROI with respect to the total integrated area |

---

## 12. Manual centroid

The **Mark manual centroid** button allows the user to click on the chromatogram and manually register a centroid position.

This function is useful for educational purposes, since it allows the user to compare a visual estimate of the peak center with the automatically calculated centroid.

---

## 13. Deleting an ROI

To delete an ROI:

1. Select a row in the **Integrated regions** table.
2. Click **Delete selected ROI**.

The program will update the table and recalculate the area percentages.

---

## 14. Exporting the chromatogram

To export chromatographic data:

1. Click **Export TIC**.
2. Choose the file name and location.
3. Save the file in `.csv` format.

The exported file contains the active chromatographic data.

---

## 15. Exporting the ROI table

To export integration results:

1. Integrate at least one ROI.
2. Click **Export ROIs**.
3. Save the `.csv` file.

The exported file contains information such as:

* Region number.
* ROI start and end.
* Centroid.
* Apex RT.
* Maximum intensity.
* Area.
* Area percentage.
* Baseline mode.

---

## 16. Saving the plot

To save the chromatogram plot:

1. Click **Save plot**.
2. Select `.png` or `.pdf` format.
3. Save the file.

---

## 17. Comparing chromatographic signals

The **Compare signals** button opens a secondary window for comparing multiple `.qgd` files.

![Comparison window](docs-en/screenshots/06_compare_window_es.png)

In this window, the user can:

* Load multiple QGD files.
* Overlay chromatographic signals.
* Normalize signals between 0 and 1.
* Apply vertical offset.
* Show or hide the legend.
* Show or hide the grid.
* Define minimum and maximum RT values.
* Export a CSV matrix with the compared signals.

---

## 18. Language selector

The interface allows the user to switch between Spanish and English using the language selector located in the application header.

![Language selector](docs-en/screenshots/07_language_selector_es.png)

When the language is changed, the interface is rebuilt and the visible texts are updated.

---

## 19. Recommended workflow

A basic workflow is:

```text
Open QGD → Visualize chromatogram → Select ROI → Integrate ROI → Export results
```

For signal comparison:

```text
Compare signals → Load multiple QGD → Normalize 0-1 → Analyze differences → Export CSV matrix
```

---

## 20. Educational interpretation of results

The program was designed to support the teaching of concepts such as:

* Retention time.
* Signal intensity.
* Peak shape.
* Area under the peak.
* Centroid.
* Peak maximum.
* Baseline correction.
* Signal smoothing.
* Comparison between chromatograms.

The integrated area can be used as a relative estimator of analyte amount, always considering the experimental conditions, chromatographic method, and signal processing applied.

---

## 21. Common issues

### The program does not open

Check that the virtual environment is activated and that all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Tkinter error on Linux

Install Tk support:

```bash
sudo apt install python3-tk
```

### The logo does not appear

Check that the logo file exists at:

```text
assets/logo_yacaspectra2.png
```

### A file cannot be opened

Check that the file has the `.qgd` extension and is not corrupted.

### The ROI cannot be integrated

Check that the selected ROI contains at least two points inside the selected interval.

---

## 22. Notes about data

`.qgd` files may contain experimental data. If they contain private, institutional, or unpublished information, they should not be uploaded to public repositories.

To share examples, include only authorized files in the folder:

```text
sample_data/
```

---

## 23. License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

---

<div align="center">

**YACA-Spectra HPLC Educational**
English user manual.

</div>
