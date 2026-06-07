"""
YACA-Spectra HPLC Educational

Educational software for teaching chromatographic signal processing,
ROI selection, peak integration, centroid calculation, and comparison of
multiple chromatographic signals.

The program is designed as a portable Tkinter desktop application and can
be packaged as a Windows executable using PyInstaller.

Main features
-------------
- Open chromatographic QGD files.
- Plot TIC-like chromatographic signals.
- Select chromatographic regions of interest.
- Calculate peak area, apex, centroid, and area percentage.
- Apply simple moving-average smoothing.
- Apply optional linear baseline correction.
- Export chromatographic data and ROI tables.
- Compare multiple chromatographic signals.
- Display ordered institutional logos in the header.

Author
------
Educational version prepared for HPLC teaching activities.
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from translations import TRANSLATIONS
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import olefile
import pandas as pd
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 720
RIGHT_PANEL_WIDTH = 430
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 620

FIG_WIDTH = 8.1
FIG_HEIGHT = 4.5
FIG_DPI = 85

BASE_FONT_SIZE = 9
TITLE_FONT_SIZE = 18
SUBTITLE_FONT_SIZE = 10
TREE_HEIGHT = 8
DEFAULT_SMOOTH_WINDOW = 1

LOGO_YACA_MAX_WIDTH = 95
LOGO_YACA_MAX_HEIGHT = 95
LOGO_FACEN_MAX_WIDTH = 230
LOGO_FACEN_MAX_HEIGHT = 70

APP_TITLE = "YACA-Spectra HPLC Educational"

COLOR_BG = "#f4f7f5"
COLOR_HEADER = "#dff1e4"
COLOR_HEADER_DARK = "#2e7d32"
COLOR_PRIMARY = "#2e7d32"
COLOR_PRIMARY_HOVER = "#1b5e20"
COLOR_SECONDARY = "#1976d2"
COLOR_SECONDARY_HOVER = "#0d47a1"
COLOR_WARNING = "#f57c00"
COLOR_WARNING_HOVER = "#e65100"
COLOR_DANGER = "#c62828"
COLOR_DANGER_HOVER = "#8e0000"
COLOR_EXPORT = "#6a1b9a"
COLOR_EXPORT_HOVER = "#4a148c"
COLOR_PANEL = "#ffffff"
COLOR_TEXT = "#1f2933"
COLOR_HINT = "#455a64"
COLOR_TREE_HEADER = "#c8e6c9"
COLOR_TREE_SELECTED = "#a5d6a7"

COLUMN_WIDTHS = {
    "region": 50,
    "rt_start_min": 78,
    "rt_end_min": 78,
    "centroid_rt_min": 92,
    "apex_rt_min": 82,
    "apex_intensity": 96,
    "area": 90,
    "area_percent": 86,
}


def resource_path(relative_path: str) -> Path:
    """Return the absolute path to an application resource.

    Parameters
    ----------
    relative_path:
        Path relative to the project folder. For example,
        ``assets/logo_yacaspectra.png``.

    Returns
    -------
    Path
        Absolute path that works in normal Python execution and also inside
        a PyInstaller executable.
    """
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def load_resized_photoimage(
    image_path: Path,
    max_width: int,
    max_height: int,
) -> ImageTk.PhotoImage:
    """Load and resize an image while preserving its aspect ratio.

    Parameters
    ----------
    image_path:
        Path to the image file.
    max_width:
        Maximum width in pixels.
    max_height:
        Maximum height in pixels.

    Returns
    -------
    ImageTk.PhotoImage
        Tkinter-compatible image resized to fit inside the selected limits.
    """
    image = Image.open(image_path)
    image = image.convert("RGBA")
    image.thumbnail((max_width, max_height), Image.LANCZOS)
    return ImageTk.PhotoImage(image)


def fit_window_to_screen(
    win: tk.Tk | tk.Toplevel,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
    min_width: int = MIN_WINDOW_WIDTH,
    min_height: int = MIN_WINDOW_HEIGHT,
) -> None:
    """Fit a Tkinter window to the available screen size.

    Parameters
    ----------
    win:
        Tkinter root or top-level window.
    width:
        Desired window width in pixels.
    height:
        Desired window height in pixels.
    min_width:
        Minimum window width in pixels.
    min_height:
        Minimum window height in pixels.

    Returns
    -------
    None
        The window geometry is updated in place.
    """
    win.update_idletasks()

    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    final_w = min(width, int(screen_w * 0.96))
    final_h = min(height, int(screen_h * 0.90))

    x = max(0, (screen_w - final_w) // 2)
    y = max(0, (screen_h - final_h) // 2)

    win.geometry(f"{final_w}x{final_h}+{x}+{y}")
    win.minsize(min_width, min_height)

    try:
        win.state("zoomed")
    except tk.TclError:
        pass


def make_scrollable_frame(parent: ttk.Frame) -> ttk.Frame:
    """Create a vertical scrollable frame.

    Parameters
    ----------
    parent:
        Parent Tkinter frame.

    Returns
    -------
    ttk.Frame
        Inner frame where widgets should be placed.
    """
    canvas = tk.Canvas(parent, highlightthickness=0, background=COLOR_BG)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)

    scrollable = ttk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")

    def on_frame_configure(event: tk.Event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfigure(window_id, width=event.width)

    def on_mousewheel(event: tk.Event) -> None:
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    scrollable.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>", on_mousewheel))
    canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))

    return scrollable


def apply_app_style(root: tk.Tk) -> None:
    """Apply a clean colored visual style to the application.

    Parameters
    ----------
    root:
        Main Tkinter root.

    Returns
    -------
    None
        The style is applied globally to Tkinter widgets.
    """
    root.option_add("*Font", ("Segoe UI", BASE_FONT_SIZE))
    root.configure(background=COLOR_BG)

    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        ".",
        background=COLOR_BG,
        foreground=COLOR_TEXT,
        fieldbackground="#ffffff",
        bordercolor="#cfd8dc",
        lightcolor="#ffffff",
        darkcolor="#b0bec5",
    )

    style.configure("TFrame", background=COLOR_BG)
    style.configure("Header.TFrame", background=COLOR_HEADER, padding=10)

    style.configure(
        "Title.TLabel",
        background=COLOR_HEADER,
        foreground=COLOR_HEADER_DARK,
        font=("Segoe UI", TITLE_FONT_SIZE, "bold"),
    )

    style.configure(
        "Subtitle.TLabel",
        background=COLOR_HEADER,
        foreground=COLOR_TEXT,
        font=("Segoe UI", SUBTITLE_FONT_SIZE),
    )

    style.configure(
        "Hint.TLabel",
        background=COLOR_BG,
        foreground=COLOR_HINT,
        font=("Segoe UI", 8),
    )

    style.configure(
        "PanelHint.TLabel",
        background=COLOR_PANEL,
        foreground=COLOR_HINT,
        font=("Segoe UI", 8),
    )

    style.configure(
        "Status.TLabel",
        background=COLOR_BG,
        foreground=COLOR_TEXT,
        font=("Segoe UI", 9),
    )

    style.configure(
        "Section.TLabelframe",
        background=COLOR_PANEL,
        foreground=COLOR_TEXT,
        bordercolor="#b0bec5",
        relief="solid",
        padding=8,
    )

    style.configure(
        "Section.TLabelframe.Label",
        background=COLOR_BG,
        foreground=COLOR_HEADER_DARK,
        font=("Segoe UI", 9, "bold"),
    )

    style.configure(
        "Primary.TButton",
        background=COLOR_PRIMARY,
        foreground="white",
        borderwidth=1,
        focusthickness=2,
        focuscolor=COLOR_PRIMARY_HOVER,
        padding=(8, 5),
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    style.configure(
        "Secondary.TButton",
        background=COLOR_SECONDARY,
        foreground="white",
        borderwidth=1,
        padding=(8, 5),
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Secondary.TButton",
        background=[
            ("active", COLOR_SECONDARY_HOVER),
            ("pressed", COLOR_SECONDARY_HOVER),
        ],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    style.configure(
        "Export.TButton",
        background=COLOR_EXPORT,
        foreground="white",
        borderwidth=1,
        padding=(8, 5),
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Export.TButton",
        background=[("active", COLOR_EXPORT_HOVER), ("pressed", COLOR_EXPORT_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    style.configure(
        "Warning.TButton",
        background=COLOR_WARNING,
        foreground="white",
        borderwidth=1,
        padding=(8, 5),
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Warning.TButton",
        background=[("active", COLOR_WARNING_HOVER), ("pressed", COLOR_WARNING_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground="white",
        borderwidth=1,
        padding=(8, 5),
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Danger.TButton",
        background=[("active", COLOR_DANGER_HOVER), ("pressed", COLOR_DANGER_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    style.configure(
        "Soft.TButton",
        background="#eceff1",
        foreground=COLOR_TEXT,
        borderwidth=1,
        padding=(8, 5),
        font=("Segoe UI", 9),
    )

    style.map(
        "Soft.TButton",
        background=[("active", "#cfd8dc"), ("pressed", "#b0bec5")],
        foreground=[("active", COLOR_TEXT), ("pressed", COLOR_TEXT)],
    )

    style.configure(
        "TEntry",
        fieldbackground="#ffffff",
        foreground=COLOR_TEXT,
        bordercolor="#90a4ae",
        padding=3,
    )

    style.configure(
        "TCombobox",
        fieldbackground="#ffffff",
        foreground=COLOR_TEXT,
        arrowcolor=COLOR_HEADER_DARK,
        bordercolor="#90a4ae",
        padding=3,
    )

    style.configure(
        "Treeview",
        background="#ffffff",
        fieldbackground="#ffffff",
        foreground=COLOR_TEXT,
        rowheight=24,
        bordercolor="#cfd8dc",
    )

    style.configure(
        "Treeview.Heading",
        background=COLOR_TREE_HEADER,
        foreground=COLOR_TEXT,
        font=("Segoe UI", 8, "bold"),
        relief="flat",
    )

    style.map(
        "Treeview",
        background=[("selected", COLOR_TREE_SELECTED)],
        foreground=[("selected", "#000000")],
    )


def read_stream(path: str | Path, stream_path: list[str]) -> bytes:
    """Read a binary stream from an OLE structured file.

    Parameters
    ----------
    path:
        Path to the QGD file.
    stream_path:
        Internal OLE stream path as a list of names.

    Returns
    -------
    bytes
        Raw bytes from the requested stream.

    Raises
    ------
    ValueError
        If the requested stream is not found in the file.
    """
    with olefile.OleFileIO(str(path)) as ole:
        stream = "/".join(stream_path)

        if ole.exists(stream):
            return ole.openstream(stream).read()

        raise ValueError(f"Stream {stream} not found in {path}")


def read_retention_times(path: str | Path) -> np.ndarray:
    """Read retention time values from a QGD chromatographic file.

    Parameters
    ----------
    path:
        Path to the QGD file.

    Returns
    -------
    np.ndarray
        Retention time values in milliseconds.
    """
    raw = read_stream(path, ["GCMS Raw Data", "Retention Time"])
    return np.frombuffer(raw, dtype="<i4")


def read_qgd_tic(path: str | Path) -> pd.DataFrame:
    """Read a chromatographic TIC-like signal from a QGD file.

    Parameters
    ----------
    path:
        Path to the QGD file.

    Returns
    -------
    pd.DataFrame
        Data frame containing ``rt_ms``, ``rt_min``, and ``intensity`` columns.
    """
    raw = read_stream(path, ["GCMS Raw Data", "TIC Data"])
    intensities = np.frombuffer(raw, dtype="<i8")
    rts = read_retention_times(path)

    n = min(len(rts), len(intensities))

    df = pd.DataFrame(
        {
            "rt_ms": rts[:n].astype(np.int64),
            "rt_min": (rts[:n] / 60000.0).astype(float),
            "intensity": intensities[:n].astype(float),
        }
    )

    return df.sort_values("rt_min").reset_index(drop=True)


def trapz_area(x: np.ndarray, y: np.ndarray) -> float:
    """Calculate the area under a curve using the trapezoidal rule.

    Parameters
    ----------
    x:
        Independent variable values.
    y:
        Dependent variable values.

    Returns
    -------
    float
        Integrated area.
    """
    if len(x) < 2:
        return 0.0

    return float(np.trapezoid(y, x))


def linear_baseline(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Calculate a straight baseline between the first and last ROI points.

    Parameters
    ----------
    x:
        Retention time values inside the ROI.
    y:
        Intensity values inside the ROI.

    Returns
    -------
    np.ndarray
        Linear baseline values.
    """
    if len(x) < 2:
        return np.zeros_like(y, dtype=float)

    dx = x[-1] - x[0]
    slope = (y[-1] - y[0]) / dx if dx != 0 else 0.0
    intercept = y[0] - slope * x[0]

    return slope * x + intercept


def centroid_in_region(x: np.ndarray, y: np.ndarray) -> float:
    """Calculate the chromatographic centroid of a selected region.

    Parameters
    ----------
    x:
        Retention time values inside the ROI.
    y:
        Intensity values inside the ROI.

    Returns
    -------
    float
        Centroid retention time. If the area is non-positive, the apex
        position is returned.
    """
    area = np.trapezoid(y, x)

    if area <= 0:
        return float(x[np.argmax(y)])

    return float(np.trapezoid(x * y, x) / area)


def smooth_moving_average(y: np.ndarray, window: int) -> np.ndarray:
    """Apply a simple moving-average smoothing filter.

    Parameters
    ----------
    y:
        Signal intensity values.
    window:
        Smoothing window size. Even values are converted to the next odd
        value.

    Returns
    -------
    np.ndarray
        Smoothed signal.
    """
    if window <= 1:
        return y.copy()

    window = max(1, int(window))

    if window % 2 == 0:
        window += 1

    kernel = np.ones(window, dtype=float) / window
    return np.convolve(y, kernel, mode="same")


def normalize_01(y: np.ndarray) -> np.ndarray:
    """Normalize a signal to the 0-1 interval.

    Parameters
    ----------
    y:
        Input signal.

    Returns
    -------
    np.ndarray
        Normalized signal.
    """
    y = np.asarray(y, dtype=float)
    ymin = np.nanmin(y)
    ymax = np.nanmax(y)

    if ymax - ymin == 0:
        return np.zeros_like(y)

    return (y - ymin) / (ymax - ymin)


def get_roi_data(df: pd.DataFrame, x1: float, x2: float) -> dict:
    """Extract chromatographic information from a selected ROI.

    Parameters
    ----------
    df:
        Chromatographic data frame with ``rt_min`` and ``intensity`` columns.
    x1:
        First retention time limit.
    x2:
        Second retention time limit.

    Returns
    -------
    dict
        Dictionary with ROI data, apex position, apex intensity, and centroid.

    Raises
    ------
    ValueError
        If the selected region contains fewer than two points.
    """
    lo, hi = sorted([x1, x2])
    sub = df[(df["rt_min"] >= lo) & (df["rt_min"] <= hi)].copy()

    if len(sub) < 2:
        raise ValueError("invalid_roi_points")

    x = sub["rt_min"].to_numpy(dtype=float)
    y = sub["intensity"].to_numpy(dtype=float)

    idx_max = int(np.argmax(y))
    apex_rt = float(x[idx_max])
    apex_intensity = float(y[idx_max])
    centroid = centroid_in_region(x, y)

    return {
        "sub_df": sub,
        "x": x,
        "y": y,
        "rt_start_min": float(lo),
        "rt_end_min": float(hi),
        "apex_rt_min": apex_rt,
        "apex_intensity": apex_intensity,
        "centroid_rt_min": centroid,
    }


def integrate_region(
    df: pd.DataFrame,
    x1: float,
    x2: float,
    baseline_mode: str = "none",
) -> dict:
    """Integrate a chromatographic region of interest.

    Parameters
    ----------
    df:
        Chromatographic data frame with ``rt_min`` and ``intensity`` columns.
    x1:
        First retention time limit.
    x2:
        Second retention time limit.
    baseline_mode:
        Baseline correction mode. Accepted values are ``none`` and ``linear``.

    Returns
    -------
    dict
        Integrated ROI result containing area, centroid, apex, baseline, and
        region limits.
    """
    roi = get_roi_data(df, x1, x2)

    x = roi["x"]
    y = roi["y"]

    if baseline_mode == "linear":
        baseline = linear_baseline(x, y)
        y_corr = y - baseline
        y_corr[y_corr < 0] = 0.0
    else:
        baseline = np.zeros_like(y)
        y_corr = y.copy()

    area = trapz_area(x, y_corr)
    centroid = centroid_in_region(x, y_corr)

    return {
        "rt_start_min": roi["rt_start_min"],
        "rt_end_min": roi["rt_end_min"],
        "centroid_rt_min": centroid,
        "apex_rt_min": roi["apex_rt_min"],
        "apex_intensity": roi["apex_intensity"],
        "area": area,
        "baseline_mode": baseline_mode,
        "sub_df": roi["sub_df"],
        "baseline": baseline,
        "area_percent": 0.0,
    }


class MultiSignalCompareWindow:
    """Window for comparing multiple chromatographic signals."""

    def __init__(self, parent: tk.Tk | tk.Toplevel, translator) -> None:
        self.parent = parent
        self.t = translator

        self.win = tk.Toplevel(parent)
        self.win.title(self.t("compare_window_title"))

        fit_window_to_screen(
            self.win,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_width=900,
            min_height=600,
        )

        self.signals = []
        self.selected_only_mode = False

        self.build_ui()
        self.build_plot()

    def build_ui(self) -> None:
        """Build the graphical interface for the comparison window."""
        main = ttk.Frame(self.win, padding=8)
        main.pack(fill="both", expand=True)

        header = ttk.LabelFrame(
            main,
            text=self.t("compare_window_header"),
            padding=8,
            style="Section.TLabelframe",
        )
        header.pack(fill="x", pady=(0, 8))

        ttk.Label(
            header,
            text=self.t("compare_window_description"),
            style="PanelHint.TLabel",
            wraplength=1000,
        ).pack(anchor="w")

        content = ttk.PanedWindow(main, orient="horizontal")
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content)
        right_outer = ttk.Frame(content, width=340)

        content.add(left, weight=4)
        content.add(right_outer, weight=1)

        right_outer.pack_propagate(False)
        right = make_scrollable_frame(right_outer)

        controls = ttk.LabelFrame(
            left,
            text=self.t("compare_section_controls"),
            padding=8,
            style="Section.TLabelframe",
        )
        controls.pack(fill="x", pady=(0, 8))

        button_bar = ttk.Frame(controls)
        button_bar.pack(fill="x", pady=(0, 4))

        buttons = [
            (self.t("load_multiple_qgd"), self.load_multiple_qgd, "Primary.TButton"),
            (self.t("update_plot"), self.redraw_plot, "Secondary.TButton"),
            (self.t("save_plot"), self.save_compare_plot, "Export.TButton"),
            (self.t("export_matrix_csv"), self.export_matrix, "Export.TButton"),
            (self.t("clear"), self.clear_signals, "Danger.TButton"),
        ]

        for i, (text, command, style_name) in enumerate(buttons):
            ttk.Button(
                button_bar,
                text=text,
                command=command,
                style=style_name,
            ).grid(row=0, column=i, padx=3, pady=3, sticky="ew")
            button_bar.columnconfigure(i, weight=1)

        options_grid = ttk.Frame(controls)
        options_grid.pack(fill="x")

        self.normalize_var = tk.BooleanVar(value=False)
        self.offset_var = tk.BooleanVar(value=False)
        self.legend_var = tk.BooleanVar(value=True)
        self.grid_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            options_grid,
            text=self.t("normalize_01"),
            variable=self.normalize_var,
            command=self.redraw_plot,
        ).grid(row=0, column=0, padx=4, pady=3, sticky="w")

        ttk.Checkbutton(
            options_grid,
            text=self.t("vertical_offset"),
            variable=self.offset_var,
            command=self.redraw_plot,
        ).grid(row=0, column=1, padx=4, pady=3, sticky="w")

        ttk.Checkbutton(
            options_grid,
            text=self.t("show_legend"),
            variable=self.legend_var,
            command=self.redraw_plot,
        ).grid(row=0, column=2, padx=4, pady=3, sticky="w")

        ttk.Checkbutton(
            options_grid,
            text=self.t("show_grid"),
            variable=self.grid_var,
            command=self.redraw_plot,
        ).grid(row=0, column=3, padx=4, pady=3, sticky="w")

        ttk.Label(options_grid, text=self.t("offset")).grid(
            row=1,
            column=0,
            padx=4,
            pady=3,
            sticky="e",
        )
        self.offset_value_var = tk.DoubleVar(value=1.2)
        ttk.Entry(options_grid, textvariable=self.offset_value_var, width=8).grid(
            row=1,
            column=1,
            padx=4,
            pady=3,
            sticky="w",
        )

        ttk.Label(options_grid, text=self.t("smoothing")).grid(
            row=1,
            column=2,
            padx=4,
            pady=3,
            sticky="e",
        )
        self.smooth_var = tk.IntVar(value=1)
        ttk.Entry(options_grid, textvariable=self.smooth_var, width=8).grid(
            row=1,
            column=3,
            padx=4,
            pady=3,
            sticky="w",
        )

        ttk.Label(options_grid, text=self.t("rt_min")).grid(
            row=2,
            column=0,
            padx=4,
            pady=3,
            sticky="e",
        )
        self.rt_min_var = tk.StringVar()
        ttk.Entry(options_grid, textvariable=self.rt_min_var, width=8).grid(
            row=2,
            column=1,
            padx=4,
            pady=3,
            sticky="w",
        )

        ttk.Label(options_grid, text=self.t("rt_max")).grid(
            row=2,
            column=2,
            padx=4,
            pady=3,
            sticky="e",
        )
        self.rt_max_var = tk.StringVar()
        ttk.Entry(options_grid, textvariable=self.rt_max_var, width=8).grid(
            row=2,
            column=3,
            padx=4,
            pady=3,
            sticky="w",
        )

        ttk.Button(
            options_grid,
            text=self.t("clear_rt_range"),
            command=self.clear_rt_range,
            style="Warning.TButton",
        ).grid(row=2, column=4, padx=4, pady=3, sticky="ew")

        for col in range(5):
            options_grid.columnconfigure(col, weight=1)

        self.plot_frame = ttk.LabelFrame(
            left,
            text=self.t("compare_section_plot"),
            padding=6,
            style="Section.TLabelframe",
        )
        self.plot_frame.pack(fill="both", expand=True)

        list_frame = ttk.LabelFrame(
            right,
            text=self.t("loaded_files"),
            padding=6,
            style="Section.TLabelframe",
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 8))

        columns = ("id", "file", "points", "rt_min", "rt_max")
        self.tree_compare = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=TREE_HEIGHT,
            selectmode="extended",
        )

        headings = {
            "id": self.t("compare_col_id"),
            "file": self.t("compare_col_file"),
            "points": self.t("compare_col_points"),
            "rt_min": self.t("compare_col_rt_min"),
            "rt_max": self.t("compare_col_rt_max"),
        }

        widths = {
            "id": 35,
            "file": 150,
            "points": 60,
            "rt_min": 65,
            "rt_max": 65,
        }

        for col in columns:
            self.tree_compare.heading(col, text=headings[col])
            self.tree_compare.column(col, width=widths[col], anchor="center")

        self.tree_compare.column("file", anchor="w")
        self.tree_compare.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree_compare.yview,
        )
        scroll_y.pack(side="right", fill="y")
        self.tree_compare.configure(yscrollcommand=scroll_y.set)

        actions = ttk.LabelFrame(
            right,
            text=self.t("actions"),
            padding=6,
            style="Section.TLabelframe",
        )
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(
            actions,
            text=self.t("delete_selected"),
            command=self.delete_selected_signal,
            style="Danger.TButton",
        ).pack(fill="x", pady=3)

        ttk.Button(
            actions,
            text=self.t("view_selected_only"),
            command=self.plot_selected_only,
            style="Secondary.TButton",
        ).pack(fill="x", pady=3)

        ttk.Button(
            actions,
            text=self.t("view_all"),
            command=self.plot_all,
            style="Primary.TButton",
        ).pack(fill="x", pady=3)

        info_frame = ttk.LabelFrame(
            right,
            text=self.t("educational_use"),
            padding=6,
            style="Section.TLabelframe",
        )
        info_frame.pack(fill="x")

        self.info_var = tk.StringVar(value=self.t("compare_info"))

        ttk.Label(
            info_frame,
            textvariable=self.info_var,
            wraplength=300,
            style="PanelHint.TLabel",
        ).pack(anchor="w")

    def build_plot(self) -> None:
        """Create the Matplotlib plot area for signal comparison."""
        self.fig_compare, self.ax_compare = plt.subplots(
            figsize=(FIG_WIDTH, FIG_HEIGHT),
            dpi=FIG_DPI,
        )

        self.canvas_compare = FigureCanvasTkAgg(
            self.fig_compare,
            master=self.plot_frame,
        )
        self.canvas_compare.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar_compare = NavigationToolbar2Tk(
            self.canvas_compare,
            self.plot_frame,
            pack_toolbar=False,
        )
        self.toolbar_compare.update()
        self.toolbar_compare.pack(fill="x")

        self.ax_compare.set_xlabel(self.t("rt_axis"))
        self.ax_compare.set_ylabel(self.t("intensity_axis"))
        self.ax_compare.set_title(self.t("compare_plot_title"))
        self.canvas_compare.draw_idle()

    def load_multiple_qgd(self) -> None:
        """Load multiple QGD files for comparison."""
        paths = filedialog.askopenfilenames(
            title=self.t("select_qgd_files_title"),
            filetypes=[
                (self.t("filetype_qgd"), "*.qgd"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if not paths:
            return

        loaded = 0
        errors = []

        for path in paths:
            try:
                df = read_qgd_tic(path)

                if df.empty:
                    errors.append(f"{Path(path).name}: {self.t('empty_file')}")
                    continue

                self.signals.append(
                    {
                        "path": Path(path),
                        "name": Path(path).name,
                        "df": df,
                        "visible": True,
                    }
                )

                loaded += 1

            except Exception as exc:
                errors.append(f"{Path(path).name}: {exc}")

        self.selected_only_mode = False
        self.refresh_signal_table()
        self.redraw_plot()

        message = f"{self.t('loaded_files_count')}: {loaded}"

        if errors:
            message += f"\n\n{self.t('some_files_not_loaded')}"

        self.info_var.set(message)

    def get_selected_indices(self) -> list[int]:
        """Return indices of selected signals in the comparison table."""
        selected_items = self.tree_compare.selection()
        selected_indices = []

        for item in selected_items:
            values = self.tree_compare.item(item, "values")

            if values:
                try:
                    selected_indices.append(int(values[0]) - 1)
                except ValueError:
                    pass

        return selected_indices

    def get_processed_signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply smoothing and RT filtering to a signal."""
        out = df.copy()

        try:
            window = int(self.smooth_var.get())
        except tk.TclError:
            window = 1

        if window > 1:
            out["intensity"] = smooth_moving_average(
                out["intensity"].to_numpy(dtype=float),
                window,
            )

        rt_min_text = self.rt_min_var.get().strip()

        if rt_min_text:
            try:
                out = out[out["rt_min"] >= float(rt_min_text)]
            except ValueError:
                pass

        rt_max_text = self.rt_max_var.get().strip()

        if rt_max_text:
            try:
                out = out[out["rt_min"] <= float(rt_max_text)]
            except ValueError:
                pass

        return out.reset_index(drop=True)

    def refresh_signal_table(self) -> None:
        """Refresh the comparison table."""
        for item in self.tree_compare.get_children():
            self.tree_compare.delete(item)

        for i, signal in enumerate(self.signals, start=1):
            df = signal["df"]
            self.tree_compare.insert(
                "",
                "end",
                values=(
                    i,
                    signal["name"],
                    len(df),
                    f"{df['rt_min'].min():.2f}",
                    f"{df['rt_min'].max():.2f}",
                ),
            )

    def redraw_plot(self) -> None:
        """Redraw the comparison plot."""
        self.ax_compare.clear()

        if not self.signals:
            self.ax_compare.set_xlabel(self.t("rt_axis"))
            self.ax_compare.set_ylabel(self.t("intensity_axis"))
            self.ax_compare.set_title(self.t("compare_plot_title"))
            self.canvas_compare.draw_idle()
            return

        selected_indices = self.get_selected_indices()
        indices_to_plot = (
            selected_indices
            if self.selected_only_mode and selected_indices
            else list(range(len(self.signals)))
        )

        try:
            offset_value = float(self.offset_value_var.get())
        except tk.TclError:
            offset_value = 1.2

        plotted = 0

        for plot_index, idx in enumerate(indices_to_plot):
            if 0 <= idx < len(self.signals):
                signal = self.signals[idx]
                df = self.get_processed_signal(signal["df"])

                if df.empty:
                    continue

                x = df["rt_min"].to_numpy()
                y = df["intensity"].to_numpy()

                if self.normalize_var.get():
                    y = normalize_01(y)

                if self.offset_var.get():
                    y = y + plot_index * offset_value

                self.ax_compare.plot(x, y, linewidth=1.2, label=signal["name"])
                plotted += 1

        self.ax_compare.set_xlabel(self.t("rt_axis"))
        self.ax_compare.set_ylabel(
            self.t("normalized_intensity_axis")
            if self.normalize_var.get()
            else self.t("intensity_axis")
        )
        self.ax_compare.set_title(
            f"{self.t('compare_plot_title')} ({plotted} {self.t('signals_count')})"
        )

        if self.grid_var.get():
            self.ax_compare.grid(True, alpha=0.25)

        if self.legend_var.get() and plotted > 0:
            self.ax_compare.legend(fontsize=7, loc="best")

        self.fig_compare.tight_layout()
        self.canvas_compare.draw_idle()

    def clear_rt_range(self) -> None:
        """Clear the retention time filter."""
        self.rt_min_var.set("")
        self.rt_max_var.set("")
        self.redraw_plot()

    def plot_selected_only(self) -> None:
        """Display only selected chromatographic signals."""
        self.selected_only_mode = True
        self.redraw_plot()

    def plot_all(self) -> None:
        """Display all loaded chromatographic signals."""
        self.selected_only_mode = False
        self.redraw_plot()

    def delete_selected_signal(self) -> None:
        """Delete selected chromatographic signals."""
        selected = sorted(self.get_selected_indices(), reverse=True)

        for idx in selected:
            if 0 <= idx < len(self.signals):
                del self.signals[idx]

        self.refresh_signal_table()
        self.redraw_plot()

    def clear_signals(self) -> None:
        """Remove all loaded signals from the comparison window."""
        self.signals.clear()
        self.refresh_signal_table()
        self.redraw_plot()

    def save_compare_plot(self) -> None:
        """Save the comparison plot as an image file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                (self.t("filetype_png"), "*.png"),
                (self.t("filetype_pdf"), "*.pdf"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if path:
            self.fig_compare.savefig(path, dpi=300, bbox_inches="tight")
            messagebox.showinfo(
                self.t("saved_title"),
                self.t("plot_saved"),
            )

    def export_matrix(self) -> None:
        """Export loaded signals as an interpolated CSV matrix."""
        if not self.signals:
            messagebox.showwarning(
                self.t("warning_no_signals_title"),
                self.t("warning_no_signals_message"),
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                (self.t("filetype_csv"), "*.csv"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if not path:
            return

        try:
            processed = []

            for signal in self.signals:
                df = self.get_processed_signal(signal["df"])

                if df.empty:
                    continue

                y = df["intensity"].to_numpy()

                if self.normalize_var.get():
                    y = normalize_01(y)

                processed.append(
                    {
                        "name": signal["name"],
                        "rt": df["rt_min"].to_numpy(),
                        "intensity": y,
                    }
                )

            if not processed:
                raise ValueError(self.t("no_valid_signals"))

            common_rt = processed[0]["rt"]
            out = pd.DataFrame({"rt_min": common_rt})

            for item in processed:
                out[Path(item["name"]).stem] = np.interp(
                    common_rt,
                    item["rt"],
                    item["intensity"],
                )

            out.to_csv(path, index=False)
            messagebox.showinfo(
                self.t("exported_title"),
                self.t("matrix_exported"),
            )

        except Exception as exc:
            messagebox.showerror(
                self.t("error_title"),
                str(exc),
            )


class ChromatoApp:
    """Main application for educational HPLC chromatogram analysis."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.current_language = "es"
        self.language_var = tk.StringVar(value="Español")
        self.root.title(self.t("app_title"))
        self.logo_yaca_image = None
        self.logo_facen_image = None
        self.df = None
        self.df_processed = None
        self.file_path = None
        self.regions = []

        self.roi_pick_mode = False
        self.centroid_pick_mode = False
        self.roi_clicks = []

        fit_window_to_screen(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_width=MIN_WINDOW_WIDTH,
            min_height=MIN_WINDOW_HEIGHT,
        )

        self._build_ui()
        self._build_plot()

    def _find_existing_asset(self, candidate_names: list[str]) -> Path | None:
        """Find the first existing image file inside the assets folder.

        Parameters
        ----------
        candidate_names:
            Possible file names to search inside the assets directory.

        Returns
        -------
        Path | None
            Path to the first existing asset file. If no file is found,
            ``None`` is returned.
        """
        for name in candidate_names:
            path = resource_path(f"assets/{name}")

            if path.exists():
                return path

        return None

    def change_language(self, event=None) -> None:
        """Change the interface language and rebuild the UI."""
        selected = self.language_var.get()

        if selected == "English":
            self.current_language = "en"
        else:
            self.current_language = "es"

        self.root.title(self.t("app_title"))

        self.rebuild_ui()

    def t(self, key: str) -> str:
        """Return the translated text for the current language."""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS["es"]).get(key, key)

    def rebuild_ui(self) -> None:
        """Rebuild the graphical interface after changing language."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self._build_ui()
        self._build_plot()

        self.refresh_table()
        self.update_summary()
        self.redraw_plot(reset_limits=True)

    def _load_logos(self) -> None:
        """Load the application and institutional logos.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The YACA-Spectra and FACEN logos are loaded and stored as
            Tkinter PhotoImage objects.
        """
        logo_yaca_file = self._find_existing_asset(
            [
                "logo_yacaspectra_full.png",
                "logo_yacaspectra_full(3).png",
                "yaca_logo.png",
                "logo_yacaspectra2.png",
            ]
        )
        logo_facen_file = self._find_existing_asset(
            [
                "logofacen.png",
                "logofacen(1).png",
                "logo_facen.png",
                "facen.png",
            ]
        )

        if logo_yaca_file is None:
            self.logo_yaca_image = None
        else:
            try:
                self.logo_yaca_image = load_resized_photoimage(
                    image_path=logo_yaca_file,
                    max_width=LOGO_YACA_MAX_WIDTH,
                    max_height=LOGO_YACA_MAX_HEIGHT,
                )
            except Exception:
                self.logo_yaca_image = None

        if logo_facen_file is None:
            self.logo_facen_image = None
        else:
            try:
                self.logo_facen_image = load_resized_photoimage(
                    image_path=logo_facen_file,
                    max_width=LOGO_FACEN_MAX_WIDTH,
                    max_height=LOGO_FACEN_MAX_HEIGHT,
                )
            except Exception:
                self.logo_facen_image = None

    def _build_header(self, parent: ttk.Frame) -> None:
        """Build the educational header with ordered logos.

        Parameters
        ----------
        parent:
            Parent Tkinter frame where the header will be placed.

        Returns
        -------
        None
            The header is created in the graphical interface.
        """
        header = ttk.Frame(parent, style="Header.TFrame")
        header.pack(fill="x", pady=(0, 8))

        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        self._load_logos()

        left_logo_box = ttk.Frame(header, style="Header.TFrame")
        left_logo_box.grid(row=0, column=0, sticky="w", padx=(0, 14), pady=2)

        if self.logo_yaca_image is not None:
            ttk.Label(
                left_logo_box,
                image=self.logo_yaca_image,
                background=COLOR_HEADER,
            ).pack(anchor="center")
        else:
            ttk.Label(
                left_logo_box,
                text="",
                font=("Segoe UI", 16, "bold"),
                background=COLOR_HEADER,
                foreground=COLOR_HEADER_DARK,
            ).pack(anchor="center")

        text_box = ttk.Frame(header, style="Header.TFrame")
        text_box.grid(row=0, column=1, sticky="nsew", padx=8, pady=2)

        ttk.Label(
            text_box,
            text="YACA-Spectra HPLC Educational",
            style="Title.TLabel",
        ).pack(anchor="center")

        ttk.Label(
            text_box,
            text=self.t("app_subtitle"),
            style="Subtitle.TLabel",
            wraplength=760,
            justify="center",
        ).pack(anchor="center", pady=(2, 0))

        ttk.Label(
            text_box,
            text=self.t("objective"),
            background=COLOR_HEADER,
            foreground=COLOR_HINT,
            font=("Segoe UI", 8),
            wraplength=760,
            justify="center",
        ).pack(anchor="center", pady=(3, 0))

        right_logo_box = ttk.Frame(header, style="Header.TFrame")
        right_logo_box.grid(row=0, column=2, sticky="e", padx=(14, 0), pady=2)

        if self.logo_facen_image is not None:
            ttk.Label(
                right_logo_box,
                image=self.logo_facen_image,
                background=COLOR_HEADER,
            ).pack(anchor="center")
        else:
            ttk.Label(
                right_logo_box,
                text="FACEN - UNA",
                font=("Segoe UI", 12, "bold"),
                background=COLOR_HEADER,
                foreground=COLOR_TEXT,
            ).pack(anchor="center")

        language_box = ttk.Frame(right_logo_box, style="Header.TFrame")
        language_box.pack(anchor="center", pady=(6, 0))

        ttk.Label(
            language_box,
            text=self.t("language"),
            background=COLOR_HEADER,
            foreground=COLOR_TEXT,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", padx=(0, 4))

        language_combo = ttk.Combobox(
            language_box,
            textvariable=self.language_var,
            values=["Español", "English"],
            state="readonly",
            width=9,
        )
        language_combo.pack(side="left")

        language_combo.bind("<<ComboboxSelected>>", self.change_language)

    def _build_ui(self) -> None:
        """Build the full graphical user interface."""
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill="both", expand=True)

        self._build_header(main)

        content = ttk.PanedWindow(main, orient="horizontal")
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content)
        right_outer = ttk.Frame(content, width=RIGHT_PANEL_WIDTH)

        content.add(left, weight=4)
        content.add(right_outer, weight=1)

        right_outer.pack_propagate(False)
        right = make_scrollable_frame(right_outer)

        self._build_file_panel(left)
        self._build_plot_panel(left)
        self._build_roi_panel(right)
        self._build_summary_panel(right)
        self._build_results_table(right)
        self._build_status_bar(main)

    def _build_file_panel(self, parent: ttk.Frame) -> None:
        """Build the file and processing control panel."""
        controls = ttk.LabelFrame(
            parent,
            text=self.t("section_file"),
            padding=8,
            style="Section.TLabelframe",
        )
        controls.pack(fill="x", pady=(0, 8))

        button_bar = ttk.Frame(controls)
        button_bar.pack(fill="x", pady=(0, 4))

        buttons = [
            (self.t("open_qgd"), self.load_qgd, "Primary.TButton"),
            (self.t("full_view"), self.reset_view, "Secondary.TButton"),
            (self.t("save_plot"), self.save_plot, "Export.TButton"),
            (self.t("export_tic"), self.export_tic, "Export.TButton"),
            (self.t("export_rois"), self.export_rois, "Export.TButton"),
            (self.t("compare_signals"), self.open_compare_window, "Warning.TButton"),
        ]

        for i, (text, command, style_name) in enumerate(buttons):
            ttk.Button(
                button_bar,
                text=text,
                command=command,
                style=style_name,
            ).grid(row=0, column=i, padx=3, pady=3, sticky="ew")
            button_bar.columnconfigure(i, weight=1)

        data_box = ttk.Frame(controls)
        data_box.pack(fill="x", pady=(4, 0))

        self.file_label = ttk.Label(
            data_box,
            text=self.t("no_file_loaded"),
            style="Status.TLabel",
        )
        self.file_label.grid(row=0, column=0, columnspan=5, sticky="w", padx=4, pady=3)

        ttk.Label(data_box, text=self.t("baseline_correction")).grid(
            row=1,
            column=0,
            padx=4,
            pady=3,
            sticky="e",
        )

        self.baseline_var = tk.StringVar(value="none")
        baseline_combo = ttk.Combobox(
            data_box,
            textvariable=self.baseline_var,
            values=["none", "linear"],
            state="readonly",
            width=12,
        )
        baseline_combo.grid(row=1, column=1, padx=4, pady=3, sticky="w")

        ttk.Label(data_box, text=self.t("smoothing")).grid(
            row=1,
            column=2,
            padx=4,
            pady=3,
            sticky="e",
        )

        self.smooth_var = tk.IntVar(value=DEFAULT_SMOOTH_WINDOW)
        ttk.Entry(data_box, textvariable=self.smooth_var, width=8).grid(
            row=1,
            column=3,
            padx=4,
            pady=3,
            sticky="w",
        )

        ttk.Button(
            data_box,
            text=self.t("apply_smoothing"),
            command=self.apply_processing,
            style="Secondary.TButton",
        ).grid(row=1, column=4, padx=4, pady=3, sticky="ew")

        for col in range(5):
            data_box.columnconfigure(col, weight=1)

        ttk.Label(
            controls,
            text=self.t("educational_note"),
            style="PanelHint.TLabel",
            wraplength=1000,
        ).pack(anchor="w", pady=(4, 0))

    def _build_plot_panel(self, parent: ttk.Frame) -> None:
        """Build the chromatogram plotting panel."""
        self.plot_frame = ttk.LabelFrame(
            parent,
            text=self.t("section_plot"),
            padding=6,
            style="Section.TLabelframe",
        )
        self.plot_frame.pack(fill="both", expand=True)

    def _build_roi_panel(self, parent: ttk.Frame) -> None:
        """Build the ROI selection and calculation panel."""
        roi_frame = ttk.LabelFrame(
            parent,
            text=self.t("section_roi"),
            padding=8,
            style="Section.TLabelframe",
        )
        roi_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(
            roi_frame,
            text=self.t("roi_instruction"),
            style="PanelHint.TLabel",
            wraplength=310,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=3, pady=(0, 5))

        fields = [
            (self.t("roi_start"), "x1_var"),
            (self.t("roi_end"), "x2_var"),
            (self.t("centroid"), "centroid_var"),
            (self.t("apex_rt"), "apex_rt_var"),
            (self.t("apex_intensity"), "apex_int_var"),
        ]

        for i, (label, var_name) in enumerate(fields, start=1):
            ttk.Label(roi_frame, text=label).grid(
                row=i,
                column=0,
                sticky="e",
                padx=3,
                pady=3,
            )
            setattr(self, var_name, tk.StringVar())
            ttk.Entry(
                roi_frame,
                textvariable=getattr(self, var_name),
                width=16,
            ).grid(row=i, column=1, sticky="ew", padx=3, pady=3)

        roi_frame.columnconfigure(1, weight=1)

        button_box = ttk.Frame(roi_frame)
        button_box.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Button(
            button_box,
            text=self.t("create_roi"),
            command=self.activate_roi_pick,
            style="Primary.TButton",
        ).pack(fill="x", pady=2)

        ttk.Button(
            button_box,
            text=self.t("manual_centroid"),
            command=self.activate_centroid_pick,
            style="Warning.TButton",
        ).pack(fill="x", pady=2)

        ttk.Button(
            button_box,
            text=self.t("integrate_roi"),
            command=self.integrate_current_roi,
            style="Secondary.TButton",
        ).pack(fill="x", pady=2)

    def _build_summary_panel(self, parent: ttk.Frame) -> None:
        """Build the educational summary panel."""
        summary = ttk.LabelFrame(
            parent,
            text=self.t("section_summary"),
            padding=8,
            style="Section.TLabelframe",
        )
        summary.pack(fill="x", pady=(0, 8))

        self.n_rois_var = tk.StringVar(value=f"{self.t('integrated_rois')}: 0")
        self.total_area_var = tk.StringVar(value=f"{self.t('total_area')}: 0.00")
        self.current_file_var = tk.StringVar(
            value=f"{self.t('file')}: {self.t('not_loaded')}"
        )

        ttk.Label(summary, textvariable=self.n_rois_var).pack(anchor="w", pady=1)
        ttk.Label(summary, textvariable=self.total_area_var).pack(anchor="w", pady=1)
        ttk.Label(summary, textvariable=self.current_file_var, wraplength=310).pack(
            anchor="w",
            pady=1,
        )

        ttk.Label(
            summary,
            text=self.t("summary_interpretation"),
            style="PanelHint.TLabel",
            wraplength=310,
        ).pack(anchor="w", pady=(5, 0))

    def _build_results_table(self, parent: ttk.Frame) -> None:
        """Build the integrated ROI table."""
        table_frame = ttk.LabelFrame(
            parent,
            text=self.t("section_table"),
            padding=6,
            style="Section.TLabelframe",
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 8))

        columns = (
            "region",
            "rt_start_min",
            "rt_end_min",
            "centroid_rt_min",
            "apex_rt_min",
            "apex_intensity",
            "area",
            "area_percent",
        )

        column_labels = {
            "region": self.t("col_region"),
            "rt_start_min": self.t("col_start"),
            "rt_end_min": self.t("col_end"),
            "centroid_rt_min": self.t("col_centroid"),
            "apex_rt_min": self.t("col_apex_rt"),
            "apex_intensity": self.t("col_apex_intensity"),
            "area": self.t("col_area"),
            "area_percent": self.t("col_area_percent"),
        }

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=TREE_HEIGHT,
        )

        for col in columns:
            self.tree.heading(col, text=column_labels[col])
            self.tree.column(col, width=COLUMN_WIDTHS.get(col, 70), anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        scroll_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        ttk.Button(
            parent,
            text=self.t("delete_selected_roi"),
            command=self.delete_selected_roi,
            style="Danger.TButton",
        ).pack(fill="x", pady=(0, 4))

    def _build_status_bar(self, parent: ttk.Frame) -> None:
        """Build the status bar."""
        status = ttk.Frame(parent)
        status.pack(fill="x", pady=(5, 0))

        self.mode_label = ttk.Label(
            status,
            text=self.t("mode_normal"),
            style="Status.TLabel",
        )
        self.mode_label.pack(side="left")

        self.help_label = ttk.Label(
            status,
            text=self.t("suggested_flow"),
            style="Hint.TLabel",
        )
        self.help_label.pack(side="right")

    def _build_plot(self) -> None:
        """Create the Matplotlib figure for the main chromatogram."""
        self.fig, self.ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=FIG_DPI)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            self.plot_frame,
            pack_toolbar=False,
        )
        self.toolbar.update()
        self.toolbar.pack(fill="x")

        self.canvas.mpl_connect("button_press_event", self.on_plot_click)

        self.ax.set_xlabel(self.t("rt_axis"))
        self.ax.set_ylabel(self.t("intensity_axis"))
        self.ax.set_title(self.t("plot_title"))
        self.canvas.draw_idle()

    def open_compare_window(self) -> None:
        """Open the multiple-signal comparison window."""
        MultiSignalCompareWindow(self.root, self.t)

    def get_active_df(self) -> pd.DataFrame | None:
        """Return the current active data frame."""
        return self.df_processed if self.df_processed is not None else self.df

    def update_area_percentages(self) -> None:
        """Update area percentages for all integrated ROIs."""
        total = sum(region["area"] for region in self.regions)

        for region in self.regions:
            region["area_percent"] = (
                100.0 * region["area"] / total if total > 0 else 0.0
            )

    def update_summary(self) -> None:
        """Update summary labels."""
        total_area = sum(region["area"] for region in self.regions)

        self.n_rois_var.set(f"{self.t('integrated_rois')}: {len(self.regions)}")
        self.total_area_var.set(f"{self.t('total_area')}: {total_area:.4e}")

        if self.file_path is not None:
            self.current_file_var.set(f"{self.t('file')}: {self.file_path.name}")
        else:
            self.current_file_var.set(f"{self.t('file')}: {self.t('not_loaded')}")

    def clear_roi_fields(self) -> None:
        """Clear the ROI entry fields."""
        for variable in [
            self.x1_var,
            self.x2_var,
            self.centroid_var,
            self.apex_rt_var,
            self.apex_int_var,
        ]:
            variable.set("")

    def load_qgd(self) -> None:
        """Load one QGD chromatographic file."""
        path = filedialog.askopenfilename(
            title=self.t("open_qgd_dialog_title"),
            filetypes=[
                (self.t("filetype_qgd"), "*.qgd"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if not path:
            return

        try:
            self.df = read_qgd_tic(path)
            self.df_processed = None
            self.file_path = Path(path)

            self.file_label.config(
                text=f"{self.t('file_loaded')}: {self.file_path.name}"
            )

            self.regions.clear()
            self.clear_roi_fields()
            self.refresh_table()
            self.update_summary()
            self.redraw_plot(reset_limits=True)

        except Exception as exc:
            messagebox.showerror(self.t("error_load_qgd"), str(exc))

    def apply_processing(self) -> None:
        """Apply smoothing to the loaded chromatographic signal."""
        if self.df is None:
            messagebox.showwarning(
                self.t("warning_no_data_title"),
                self.t("warning_load_qgd"),
            )
            return

        try:
            window = int(self.smooth_var.get())
        except tk.TclError:
            window = DEFAULT_SMOOTH_WINDOW

        df2 = self.df.copy()
        df2["intensity"] = smooth_moving_average(
            df2["intensity"].to_numpy(),
            window,
        )

        self.df_processed = df2
        self.redraw_plot(reset_limits=True)

    def activate_roi_pick(self) -> None:
        """Activate two-click ROI selection mode."""
        if self.get_active_df() is None:
            messagebox.showwarning(
                self.t("warning_no_data_title"),
                self.t("warning_load_chromatogram"),
            )
            return

        self.roi_pick_mode = True
        self.centroid_pick_mode = False
        self.roi_clicks = []
        self.mode_label.config(text=self.t("mode_roi_active"))
        self.help_label.config(text=self.t("help_first_second_click"))

    def activate_centroid_pick(self) -> None:
        """Activate manual centroid marking mode."""
        if self.get_active_df() is None:
            messagebox.showwarning(
                self.t("warning_no_data_title"),
                self.t("warning_load_chromatogram"),
            )
            return

        self.centroid_pick_mode = True
        self.roi_pick_mode = False
        self.mode_label.config(text=self.t("mode_manual_centroid"))
        self.help_label.config(text=self.t("help_mark_centroid"))

    def on_plot_click(self, event) -> None:
        """Handle mouse clicks on the chromatogram."""
        if event.inaxes != self.ax or event.xdata is None:
            return

        x = float(event.xdata)

        if self.roi_pick_mode:
            self.roi_clicks.append(x)

            if len(self.roi_clicks) == 1:
                self.mode_label.config(text=self.t("mode_roi_second_limit"))
                return

            if len(self.roi_clicks) == 2:
                x1, x2 = sorted(self.roi_clicks)

                try:
                    roi = get_roi_data(self.get_active_df(), x1, x2)
                except Exception:
                    messagebox.showerror(
                        self.t("error_invalid_roi_title"),
                        self.t("error_invalid_roi_points"),
                    )
                    self.roi_pick_mode = False
                    self.roi_clicks = []
                    self.mode_label.config(text=self.t("mode_normal"))
                    return

                self.x1_var.set(f"{x1:.4f}")
                self.x2_var.set(f"{x2:.4f}")
                self.centroid_var.set(f"{roi['centroid_rt_min']:.4f}")
                self.apex_rt_var.set(f"{roi['apex_rt_min']:.4f}")
                self.apex_int_var.set(f"{roi['apex_intensity']:.0f}")

                self.roi_pick_mode = False
                self.roi_clicks = []
                self.mode_label.config(text=self.t("mode_normal"))
                self.help_label.config(text=self.t("help_roi_defined"))
                self.redraw_plot()
                return

        if self.centroid_pick_mode:
            self.centroid_var.set(f"{x:.4f}")
            self.centroid_pick_mode = False
            self.mode_label.config(text=self.t("mode_normal"))
            self.help_label.config(text=self.t("help_centroid_registered"))
            self.redraw_plot()

    def integrate_current_roi(self) -> None:
        """Integrate the currently selected ROI."""
        df = self.get_active_df()

        if df is None:
            messagebox.showwarning(
                self.t("warning_no_data_title"),
                self.t("warning_load_chromatogram"),
            )
            return

        try:
            x1 = float(self.x1_var.get())
            x2 = float(self.x2_var.get())
        except ValueError:
            messagebox.showerror(
                self.t("error_incomplete_roi_title"),
                self.t("error_incomplete_roi_message"),
            )
            return

        try:
            result = integrate_region(
                df=df,
                x1=x1,
                x2=x2,
                baseline_mode=self.baseline_var.get(),
            )

            result["region"] = len(self.regions) + 1
            self.regions.append(result)

            self.refresh_table()
            self.update_summary()
            self.redraw_plot()

        except Exception as exc:
            error_message = (
                self.t("error_invalid_roi_points")
                if str(exc) == "invalid_roi_points"
                else str(exc)
            )

            messagebox.showerror(
                self.t("error_integration_title"),
                error_message,
            )

    def refresh_table(self) -> None:
        """Refresh the integrated ROI results table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.update_area_percentages()

        for region in self.regions:
            self.tree.insert(
                "",
                "end",
                values=(
                    region["region"],
                    f"{region['rt_start_min']:.3f}",
                    f"{region['rt_end_min']:.3f}",
                    f"{region['centroid_rt_min']:.3f}",
                    f"{region['apex_rt_min']:.3f}",
                    f"{region['apex_intensity']:.0f}",
                    f"{region['area']:.4e}",
                    f"{region['area_percent']:.2f}",
                ),
            )

        self.update_summary()

    def on_tree_select(self, event=None) -> None:
        """Handle ROI table row selection."""
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        if not values:
            return

        region_id = int(values[0])

        for region in self.regions:
            if region["region"] == region_id:
                self.x1_var.set(f"{region['rt_start_min']:.4f}")
                self.x2_var.set(f"{region['rt_end_min']:.4f}")
                self.centroid_var.set(f"{region['centroid_rt_min']:.4f}")
                self.apex_rt_var.set(f"{region['apex_rt_min']:.4f}")
                self.apex_int_var.set(f"{region['apex_intensity']:.0f}")
                self.redraw_plot()
                break

    def redraw_plot(self, reset_limits: bool = False) -> None:
        """Redraw the main chromatogram."""
        self.ax.clear()
        df = self.get_active_df()

        if df is not None:
            self.ax.plot(
                df["rt_min"],
                df["intensity"],
                linewidth=1.3,
                label=self.t("chromatogram_label"),
                color=COLOR_PRIMARY,
            )

            for region in self.regions:
                self.ax.axvspan(
                    region["rt_start_min"],
                    region["rt_end_min"],
                    alpha=0.20,
                    color=COLOR_WARNING,
                )
                self.ax.axvline(
                    region["centroid_rt_min"],
                    linestyle="--",
                    linewidth=1.0,
                    alpha=0.85,
                    color=COLOR_DANGER,
                )
                self.ax.text(
                    region["apex_rt_min"],
                    region["apex_intensity"],
                    f"ROI {region['region']}",
                    fontsize=8,
                    ha="center",
                    va="bottom",
                    color=COLOR_DANGER,
                )

            if self.x1_var.get() and self.x2_var.get():
                try:
                    x1 = float(self.x1_var.get())
                    x2 = float(self.x2_var.get())
                    lo, hi = sorted([x1, x2])
                    self.ax.axvspan(lo, hi, alpha=0.12, color=COLOR_SECONDARY)
                except ValueError:
                    pass

            if reset_limits:
                self.ax.relim()
                self.ax.autoscale()

        self.ax.set_xlabel(self.t("rt_axis"))
        self.ax.set_ylabel(self.t("intensity_axis"))
        self.ax.set_title(self.t("plot_title"))
        self.ax.grid(True, alpha=0.20)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def reset_view(self) -> None:
        """Reset the chromatogram view to the full signal range."""
        self.redraw_plot(reset_limits=True)

    def save_plot(self) -> None:
        """Save the current chromatogram plot."""
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                (self.t("filetype_png"), "*.png"),
                (self.t("filetype_pdf"), "*.pdf"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if path:
            self.fig.savefig(path, dpi=300, bbox_inches="tight")
            messagebox.showinfo(
                self.t("saved_title"),
                self.t("plot_saved"),
            )

    def delete_selected_roi(self) -> None:
        """Delete the selected ROI from the results table."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                self.t("warning_no_selection_title"),
                self.t("warning_select_roi_to_delete"),
            )
            return

        region_id = int(self.tree.item(selected[0], "values")[0])

        self.regions = [
            region for region in self.regions if region["region"] != region_id
        ]

        for i, region in enumerate(self.regions, start=1):
            region["region"] = i

        self.refresh_table()
        self.update_summary()
        self.redraw_plot()

    def export_tic(self) -> None:
        """Export the active chromatographic signal to CSV."""
        df = self.get_active_df()

        if df is None:
            messagebox.showwarning(
                self.t("warning_no_data_title"),
                self.t("warning_load_chromatogram"),
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                (self.t("filetype_csv"), "*.csv"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if path:
            df.to_csv(path, index=False)
            messagebox.showinfo(
                self.t("exported_title"),
                self.t("tic_exported"),
            )

    def export_rois(self) -> None:
        """Export integrated ROI results to CSV."""
        if not self.regions:
            messagebox.showwarning(
                self.t("warning_no_rois_title"),
                self.t("warning_no_rois_message"),
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                (self.t("filetype_csv"), "*.csv"),
                (self.t("filetype_all"), "*.*"),
            ],
        )

        if not path:
            return

        export_rows = []

        for region in self.regions:
            export_rows.append(
                {
                    "region": region["region"],
                    "rt_start_min": region["rt_start_min"],
                    "rt_end_min": region["rt_end_min"],
                    "centroid_rt_min": region["centroid_rt_min"],
                    "apex_rt_min": region["apex_rt_min"],
                    "apex_intensity": region["apex_intensity"],
                    "area": region["area"],
                    "area_percent": region["area_percent"],
                    "baseline_mode": region["baseline_mode"],
                }
            )

        pd.DataFrame(export_rows).to_csv(path, index=False)
        messagebox.showinfo(
            self.t("exported_title"),
            self.t("rois_exported"),
        )


def main() -> None:
    """Run the YACA-Spectra HPLC Educational application."""
    root = tk.Tk()
    apply_app_style(root)
    ChromatoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
