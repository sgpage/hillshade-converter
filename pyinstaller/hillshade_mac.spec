# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Hillshade Converter - macOS
Build: python -m PyInstaller pyinstaller/hillshade_mac.spec --noconfirm
"""

import os
import glob

# ── Detect osgeo (GDAL Python bindings) from the active Python environment ──
try:
    import osgeo as _osgeo_mod
    osgeo_dir = os.path.dirname(_osgeo_mod.__file__)
except ImportError:
    raise SystemError(
        "osgeo (GDAL Python bindings) not found in the active Python environment.\n"
        "Fix: add the Homebrew GDAL site-packages to your venv via a .pth file:\n"
        "  echo /opt/homebrew/Cellar/gdal/<version>/lib/python3.XX/site-packages "
        "> .venv/lib/python3.XX/site-packages/homebrew_gdal.pth"
    )

print(f"[spec] osgeo_dir = {osgeo_dir}")

# .so extension modules → binaries (PyInstaller collects dylib deps transitively)
osgeo_binaries = [
    (so, "osgeo")
    for so in glob.glob(os.path.join(osgeo_dir, "*.so"))
]

# Pure-Python files → datas
osgeo_datas = [
    (py, "osgeo")
    for py in glob.glob(os.path.join(osgeo_dir, "*.py"))
]

# ── GDAL CLI tools needed by the app (called via subprocess) ──
_gdal_bin = "/opt/homebrew/bin"
_gdal_cli = ["gdaldem", "gdalinfo", "gdal_translate", "gdalwarp"]
gdal_binaries = [
    (os.path.join(_gdal_bin, tool), "bin")
    for tool in _gdal_cli
    if os.path.exists(os.path.join(_gdal_bin, tool))
]

# ── GDAL/PROJ data files (coordinate transforms, projections, etc.) ──
_gdal_data_src = "/opt/homebrew/share/gdal"
_proj_data_src = "/opt/homebrew/share/proj"
extra_datas = []
if os.path.isdir(_gdal_data_src):
    extra_datas.append((_gdal_data_src, "gdal_data"))
if os.path.isdir(_proj_data_src):
    extra_datas.append((_proj_data_src, "proj_data"))

a = Analysis(
    ["../hillshade_converter.py"],
    pathex=[],
    binaries=osgeo_binaries + gdal_binaries,
    datas=osgeo_datas + extra_datas,
    hiddenimports=["PIL"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="hillshade_converter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name="Hillshade Converter.app",
    icon=None,
    bundle_identifier="co.pagetech.hillshade-converter",
    info_plist={
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": "True",
        "NSRequiresIPhoneOS": False,
    },
)
