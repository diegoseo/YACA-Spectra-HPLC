<div align="center">

<img src="assets/logo_yacaspectra2.png" alt="Logo de YACA-Spectra" width="180"/>

# YACA-Spectra HPLC Educational

### Software educativo de escritorio para visualización de cromatogramas HPLC/QGD, selección de ROI, integración de picos, cálculo de centroide y comparación de señales cromatográficas.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![Platform](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Estado-Educativo-orange)
![License](https://img.shields.io/badge/Licencia-MIT-purple)

[English](README.md)

</div>

---

## Descripción general

**YACA-Spectra HPLC Educational** es una aplicación de escritorio desarrollada en Python para actividades educativas relacionadas con el análisis de señales cromatográficas.

El software permite cargar archivos cromatográficos `.qgd`, visualizar cromatogramas tipo TIC, seleccionar regiones de interés, integrar picos, calcular centroide y valores de máximo de pico, estimar porcentajes de área y comparar múltiples señales cromatográficas.

---

## Características principales

| Módulo                 | Descripción                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| Carga de datos         | Apertura de archivos cromatográficos `.qgd`                              |
| Visualización          | Representación del cromatograma como intensidad vs. tiempo de retención  |
| Selección de ROI       | Selección de regiones de interés usando dos clics del mouse              |
| Integración de picos   | Cálculo de área, centroide, RT máximo e intensidad máxima                |
| Procesamiento          | Suavizado por media móvil y corrección lineal de línea base              |
| Exportación            | Exportación de cromatogramas y tablas de ROI en archivos CSV             |
| Comparación de señales | Comparación de múltiples señales cromatográficas en una ventana dedicada |
| Idioma                 | Interfaz disponible en español e inglés                                  |

---

## Estructura del proyecto

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

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/diegoseo/YACA-Spectra-HPLC.git
cd YACA-Spectra-HPLC
```

### 2. Crear un entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Ejecución

Ejecutar la aplicación con:

```bash
python yaca_spectra.py
```

---

## Dependencias

Las principales dependencias del proyecto son:

```text
numpy
pandas
matplotlib
pillow
olefile
```

Todas las dependencias necesarias están listadas en el archivo `requirements.txt`.

---

## Flujo básico de uso

1. Abrir la aplicación.
2. Hacer clic en **Abrir QGD**.
3. Seleccionar un archivo cromatográfico `.qgd`.
4. Visualizar el cromatograma.
5. Seleccionar una región de interés usando dos clics.
6. Integrar el pico seleccionado.
7. Exportar el cromatograma, exportar los resultados de ROI o comparar múltiples señales.

---

## Datos de ejemplo

Los archivos de ejemplo pueden incluirse en la carpeta:

```text
sample_data/
```

Si los archivos `.qgd` contienen datos privados, institucionales o de laboratorio, se recomienda no subirlos a un repositorio público.

---

## Notas importantes

* Este software usa **Tkinter**, por lo tanto debe ejecutarse en un entorno con interfaz gráfica.
* En Linux, si aparece un error relacionado con Tkinter, instala el soporte correspondiente:

```bash
sudo apt install python3-tk
```

* Si las imágenes de los logos no están disponibles, el programa puede ejecutarse usando textos de reemplazo.
* Los archivos de entrada esperados son cromatogramas con extensión `.qgd`.

---

## Propósito educativo

YACA-Spectra HPLC Educational fue diseñado para apoyar la enseñanza de conceptos relacionados con:

* Tiempo de retención.
* Identificación de picos cromatográficos.
* Selección de regiones de interés.
* Integración de picos.
* Área relativa de pico.
* Cálculo de centroide y máximo de pico.
* Corrección de línea base.
* Suavizado de señales.
* Comparación de perfiles cromatográficos.

---

## Descargas

Las versiones ejecutables están disponibles en la sección [Releases](../../releases).

### Archivos de la última versión

| Sistema operativo | Archivo                          |
| ----------------- | -------------------------------- |
| Linux             | `YACA-Spectra-HPLC-Linux.tar.gz` |
| Windows           | `YACA-Spectra-HPLC-Windows.exe`  |
| macOS             | `YACA-Spectra-HPLC-macOS.zip`    |

### Ejecución en Linux

Descargue `YACA-Spectra-HPLC-Linux.tar.gz`, extraiga el archivo, otorgue permiso de ejecución y abra la aplicación:

```bash
tar -xzf YACA-Spectra-HPLC-Linux.tar.gz
chmod +x YACA-Spectra-HPLC-Linux
./YACA-Spectra-HPLC-Linux
```

### Ejecución en Windows

Descargue y ejecute:

```text
YACA-Spectra-HPLC-Windows.exe
```

Si Windows muestra una advertencia de seguridad, seleccione **Más información → Ejecutar de todos modos** únicamente si descargó el archivo desde la página oficial de releases del proyecto.

### Ejecución en macOS

Descargue y extraiga:

```text
YACA-Spectra-HPLC-macOS.zip
```

Luego abra el archivo `.app`. Si macOS muestra una advertencia de seguridad porque la aplicación no está firmada ni notarizada, use **clic derecho → Abrir**.

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulte el archivo `LICENSE` para más información.

---

<div align="center">

**YACA-Spectra HPLC Educational**
Software educativo para análisis de señales cromatográficas.

</div>
