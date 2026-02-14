# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FlatCAM is a 2D Computer-Aided Manufacturing (CAM) application for PCB fabrication on CNC routers. It processes Gerber files (PCB layouts), Excellon files (drill data), and SVG files to generate G-Code for isolation routing, drilling, and milling. Built with Python 3, PyQt5, and VisPy (OpenGL visualization).

## Running the Application

```bash
python FlatCAM.py
```

## Running Tests

Tests use Python's `unittest` framework. Most tests require a running PyQt5 QApplication.

```bash
# Run all tests
python -m unittest discover tests

# Run a single test file
python -m unittest tests.test_excellon
python -m unittest tests.test_gerber_flow

# Run a specific test case
python -m unittest tests.test_excellon.ExcellonNumberParseTestInch

# Run Tcl command tests
python -m unittest discover tests/test_tclCommands
```

Key required test: `test_gerber_flow.py` covers the Gerber-to-GCode generation workflow and is marked as required for any updates.

## Installing Dependencies

```bash
# Ubuntu/Debian
sudo bash setup_ubuntu.sh

# pip-installable dependencies
pip3 install -r requirements.txt
```

PyQt5 can be installed via pip (`pip3 install PyQt5`) or system package manager (`python3-pyqt5`).

## Architecture

### Core Layer: `camlib.py`

Pure geometry and manufacturing logic, independent of the GUI:
- **`Geometry`** - Base class for all geometric operations (buffer, offset, scale, mirror)
- **`Gerber(Geometry)`** - Gerber RS-274X parser with aperture handling
- **`Excellon(Geometry)`** - Excellon/NC drill file parser
- **`CNCjob(Geometry)`** - G-Code generation (isolation routing, drilling, milling)
- **`ApertureMacro`** - Gerber aperture macro definitions
- **`FlatCAMRTree`** - R-tree spatial indexing for geometry queries

### Application Layer: `FlatCAMApp.py`

The `App` class is the central orchestrator (~4300 lines). It manages:
- File I/O (`open_gerber()`, `open_excellon()`, `open_gcode()`, `open_project()`)
- Object lifecycle (`new_object()`, `delete_object()`)
- Worker thread dispatch for background processing
- Tcl shell integration for scripting
- Global defaults via `LoudDict` (a dict subclass with change callbacks)

### Object Hierarchy: `FlatCAMObj.py`

Each file type has a corresponding FlatCAM object that wraps a `camlib` class with Qt integration:

```
FlatCAMObj (QObject base)
├── FlatCAMGerber    → wraps camlib.Gerber
├── FlatCAMGeometry  → wraps camlib.Geometry
├── FlatCAMExcellon  → wraps camlib.Excellon
└── FlatCAMCNCjob    → wraps camlib.CNCjob
```

Objects live in an `ObjectCollection` (Qt model/view pattern) shown in the Project panel.

### Visualization: VisPy/OpenGL

- **`PlotCanvas`** - Main canvas widget integrating VisPy into PyQt5
- **`VisPyCanvas`** - Low-level VisPy scene setup (camera, grid, axes)
- **`VisPyVisuals`** - GPU-accelerated `ShapeCollection` and `TextCollection` for rendering geometry
- **`VisPyPatches`** - Monkey-patches applied to VisPy at startup (must be applied before canvas creation)

### GUI: PyQt5

- **`FlatCAMGUI`** - Menu bar, toolbars, and main window layout
- **`GUIElements.py`** - Custom Qt widgets: `FloatEntry`, `LengthEntry`, `IntEntry`, `RadioSet`, `FCCheckBox`, `OptionalInputSection`
- **`ObjectUI.py`** - Per-object-type property panels (`GerberObjectUI`, `GeometryObjectUI`, etc.)
- **`FlatCAMDraw`** - Interactive drawing/editing tools for geometry manipulation

### Tcl Scripting: `tclCommands/`

Extensible command system for batch/scripted operations:
- **`TclCommand`** - Base class with ordered `arg_names`, `option_types`, validation, and help generation
- Commands: `open_gerber`, `open_excellon`, `isolate`, `cncjob`, `drillcncjob`, `export_gcode`, `import_svg`, `add_polygon`, `add_polyline`, `exteriors`, `interiors`, `new`, `new_geometry`

### Threading Model

- **`FlatCAMWorkerStack`** - Manages 2 `QThread`-based workers to prevent UI blocking
- **`FlatCAMWorker`** - Processes tasks from a queue within a Qt event loop
- **`FlatCAMProcess`** - Context managers for tracking active background operations with progress callbacks
- **`FlatCAMPool`** - `multiprocessing.Pool` wrapper for CPU-intensive Shapely geometry operations

## Key Patterns

- **Signal/slot communication**: `App` emits signals (`inform`, `worker_task`, `file_opened`, `progress`, `plots_updated`) rather than calling UI directly
- **Options propagation**: `App.defaults` (global) and `FlatCAMObj.options` (per-object) are `LoudDict` instances that fire callbacks on changes, keeping UI in sync
- **Never call GUI from worker threads**: All GUI updates go through Qt signals; worker threads only process data

## Primary Manufacturing Workflow

```
Gerber/Excellon File → Parse → FlatCAMObj (in collection)
  → Configure parameters (tool dia, passes, feed rates)
  → Generate CNC job → FlatCAMCNCjob
  → Export G-Code → .nc/.gcode file
```

## Building & Releasing

### PyInstaller (Linux/Windows)

```bash
pip install pyinstaller PyOpenGL PyOpenGL-accelerate
pyinstaller flatcam.spec --noconfirm
```

Key files:
- **`flatcam.spec`** - PyInstaller spec file (cross-platform, `--onedir` mode). Bundles `share/`, `tclCommands/`, `descartes/`, VisPy data files. Handles hidden imports for dynamically-loaded tclCommands, vispy backends, and OpenGL platform modules.
- **`pyinstaller-hooks/runtime_hook.py`** - Sets CWD to executable directory in frozen builds so relative `share/` paths resolve correctly.

### Arch/Manjaro package

```bash
makepkg -s
sudo pacman -U flatcam-*.pkg.tar.zst
```

The **`PKGBUILD`** installs to `/opt/flatcam/` with pip-managed Python deps in `/opt/flatcam/lib/`, a `/usr/bin/flatcam` launcher, and a `.desktop` file.

### CI/CD: GitHub Actions

**`.github/workflows/release.yml`** triggers on `v*` tag pushes and runs three build jobs:
- `build-linux` (ubuntu-22.04) - PyInstaller `.tar.gz`
- `build-windows` (windows-latest) - PyInstaller `.zip`
- `build-arch` (archlinux:latest container) - `makepkg` `.pkg.tar.zst`

A `release` job then publishes all artifacts as GitHub Release assets.

To create a release: `git tag v8.5 && git push origin v8.5`

### Windows (cx_Freeze, legacy)

```bash
python make_win32.py build
```

Uses cx_Freeze to package the application with all dependencies.

### Frozen build support

`FlatCAMApp.py` detects `sys.frozen` (set by PyInstaller/cx_Freeze) and resolves `app_home` from `sys.executable` instead of `__file__`, so icon and data paths work correctly in bundled builds.
