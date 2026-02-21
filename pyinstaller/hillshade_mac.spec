# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Hillshade Converter - macOS
Build: pyinstaller pyinstaller/hillshade_mac.spec
"""

a = Analysis(
    ["../hillshade_converter.py"],
    pathex=[],
    binaries=[],
    datas=[],
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
