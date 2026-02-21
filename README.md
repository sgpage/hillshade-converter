# Hillshade Converter

Convert GeoTIFF DEM (Digital Elevation Model) files to offline hillshade MBTiles for use in mapping applications.

## Features

- 🗺️ Converts GeoTIFF DEM files to hillshade MBTiles tiles
- 👁️ Real-time preview of hillshade with adjustable parameters
- ⚙️ Configurable shading parameters (Z-factor, azimuth, altitude, zoom levels)
- 📦 Standalone executables for macOS and Windows (no Python installation required)
- 🔐 Code-signed macOS builds for trusted distribution

## Download

**macOS (Apple Silicon & Intel)**
- [Hillshade_Converter_macOS_arm64.tar.gz](https://github.com/pagetech/hillshade-converter/releases/download/latest/Hillshade_Converter_macOS_arm64.tar.gz)
- [Hillshade_Converter_macOS_x86_64.tar.gz](https://github.com/pagetech/hillshade-converter/releases/download/latest/Hillshade_Converter_macOS_x86_64.tar.gz)

**Windows**
- [Hillshade_Converter_Windows.zip](https://github.com/pagetech/hillshade-converter/releases/download/latest/Hillshade_Converter_Windows.zip)

## Installation

### macOS

1. Download the appropriate build for your Mac (usually ARM64 for M1/M2 Macs, x86_64 for Intel)
2. Extract the .tar.gz file
3. Move **Hillshade Converter.app** to your Applications folder
4. Run it from Applications

_Note: The first time you run it, macOS may show a security warning. Click "Open" to trust the code-signed app._

### Windows

1. Download the ZIP file
2. Extract it to a folder
3. Run **hillshade_converter.exe**

## Requirements

- **GDAL** - Geospatial Data Abstraction Library

### macOS
```bash
brew install gdal
```

### Windows
Download from: [GIS Internals](https://trac.osgeo.org/osgeo4w/)

## Usage

1. **Select Input**: Choose a GeoTIFF DEM file
2. **Set Parameters**:
   - **Z-Factor**: Vertical exaggeration (1.0 = normal, higher = more dramatic)
   - **Azimuth**: Direction of light source (0-360°)
   - **Altitude**: Angle of light (0-90°)
   - **Zoom Levels**: Min/Max zoom for tiling
3. **Preview** (optional): Generate a preview to check settings
4. **Convert**: Create the MBTiles file

The output MBTiles file can be used with mapping libraries like Mapbox GL, Leaflet, or integrated into apps like FlutterMap.

## Building from Source

### Prerequisites

- Python 3.8+
- pip
- GDAL development files
- PyInstaller

### macOS Build

```bash
# Install dependencies
pip install -r requirements.txt

# Build app
./build_scripts/build_mac.sh

# (Optional) Code-sign the app
./build_scripts/sign_mac.sh

# Package for release
tar -czf Hillshade_Converter_macOS_arm64.tar.gz -C dist Hillshade\ Converter.app
```

### Windows Build

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
build_scripts\build_windows.bat

# Package for release
7z a Hillshade_Converter_Windows.zip dist\hillshade_converter.exe
```

## Code Signing for Mac Distribution

To sign your builds with your Apple Developer certificate:

1. Install your Developer ID Application certificate in Keychain
2. Run: `./build_scripts/sign_mac.sh`
3. When prompted, enter your certificate name (e.g., "Developer ID Application: Your Name (TEAMID)")

This allows users to run the app without App Store warnings about "unidentified developers."

### Optional: Notarization

For macOS Big Sur (11.0) and later, you can notarize the app for additional trust:

```bash
# Notarize the signed app
xcrun altool --notarize-app \
  -f dist/Hillshade\ Converter.app.zip \
  -t osx \
  --file-type zip \
  --primary-bundle-id co.pagetech.hillshade-converter \
  -u your@email.com \
  -p @keychain:app-specific-password

# Wait for status (check email or use request UUID)
xcrun altool --notarization-info <REQUEST_UUID> \
  -u your@email.com \
  -p @keychain:app-specific-password
```

## License

MIT

## Support

For issues or feature requests, visit the [GitHub repository](https://github.com/pagetech/hillshade-converter).
