# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for FlatCAM.

Builds a one-directory bundle (not one-file) because the application
uses relative paths to share/ icons and other data files.

Usage:
    pyinstaller flatcam.spec --noconfirm
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Data files to bundle ──────────────────────────────────────────────

datas = [
    ('share', 'share'),
    ('tclCommands', 'tclCommands'),
    ('descartes', 'descartes'),
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# VisPy needs its GLSL shaders, colormaps, and other data files
datas += collect_data_files('vispy')

# ── Hidden imports ────────────────────────────────────────────────────

hiddenimports = [
    # tclCommands are loaded dynamically via pkgutil.walk_packages
    'tclCommands.TclCommand',
    'tclCommands.TclCommandAddPolygon',
    'tclCommands.TclCommandAddPolyline',
    'tclCommands.TclCommandCncjob',
    'tclCommands.TclCommandDrillcncjob',
    'tclCommands.TclCommandExportGcode',
    'tclCommands.TclCommandExteriors',
    'tclCommands.TclCommandImportSvg',
    'tclCommands.TclCommandInteriors',
    'tclCommands.TclCommandIsolate',
    'tclCommands.TclCommandNew',
    'tclCommands.TclCommandOpenGerber',

    # VisPy backend and submodules
    'vispy.app.backends._pyqt5',
]

hiddenimports += collect_submodules('vispy')

# OpenGL
hiddenimports += [
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.GLU',
]

if sys.platform == 'linux':
    hiddenimports += ['OpenGL.platform.glx']
elif sys.platform == 'win32':
    hiddenimports += ['OpenGL.platform.win32']

# Other libraries that may not be auto-detected
hiddenimports += [
    'simplejson',
    'svg',
    'svg.path',
    'descartes',
    'descartes.patch',
    'tkinter',
]

# Windows-specific hidden imports
if sys.platform == 'win32':
    hiddenimports += [
        'win32com.shell.shell',
        'win32com.shell.shellcon',
    ]

# ── Analysis ──────────────────────────────────────────────────────────

a = Analysis(
    ['FlatCAM.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyinstaller-hooks/runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Platform-specific EXE settings ────────────────────────────────────

if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='FlatCAM',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='share/flatcam_icon48.ico',
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='FlatCAM',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
    )

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FlatCAM',
)
