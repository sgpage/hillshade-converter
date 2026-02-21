# Hillshade Converter - Setup & Distribution Guide

## Quick Start

### 1. Create a GitHub Repository

```bash
cd /Users/stevepage/Developer/hillshade-converter
git init
git add .
git commit -m "Initial commit: Hillshade Converter project"
git remote add origin https://github.com/YOUR_USERNAME/hillshade-converter.git
git push -u origin main
```

### 2. Make Scripts Executable

```bash
chmod +x build_scripts/build_mac.sh
chmod +x build_scripts/sign_mac.sh
chmod +x build_scripts/notarize_mac.sh
```

### 3. Build Locally

#### macOS
```bash
./build_scripts/build_mac.sh
```

#### Windows
```bash
build_scripts\build_windows.bat
```

## Code Signing on macOS

### Prerequisites
1. Have an Apple Developer Account ($99/year)
2. Have a "Developer ID Application" certificate in Keychain

### Check Your Certificate

```bash
security find-certificate -c "Developer ID Application" | grep "alis" | sed 's/.*alis"\(.*\)"/\1/'
```

Example output:
```
Developer ID Application: Steve Page (ABC123DEFG)
```

### Sign Your Build

```bash
./build_scripts/sign_mac.sh
```

When prompted, enter your certificate name exactly as shown above.

### Verify Signature

```bash
codesign -d --verbose=4 "dist/Hillshade Converter.app"
```

## Notarization (Recommended)

### One-Time Setup

```bash
# Get app-specific password from https://appleid.apple.com
# Store credentials securely
xcrun notarytool store-credentials "pagetech-notary" \
  --apple-id "your@email.com" \
  --team-id "YOUR_TEAM_ID" \
  --password "xxxx-xxxx-xxxx-xxxx"
```

### Notarize Your Build

```bash
./build_scripts/notarize_mac.sh
```

This script will:
1. Create a zip archive of the signed app
2. Submit to Apple for notarization
3. Wait for approval (typically 2-5 minutes)
4. Staple the notarization ticket to the app
5. Verify Gatekeeper acceptance

## Creating Releases

### macOS Release

```bash
# Build the app
./build_scripts/build_mac.sh

# Sign it (recommended)
./build_scripts/sign_mac.sh

# Notarize it (recommended for public distribution)
./build_scripts/notarize_mac.sh

# For Apple Silicon (M1/M2/M3)
tar -czf Hillshade_Converter_macOS_arm64.tar.gz -C dist "Hillshade Converter.app"

# For Intel Macs (run build on Intel machine or with specific target)
tar -czf Hillshade_Converter_macOS_x86_64.tar.gz -C dist "Hillshade Converter.app"
```

### Windows Release

```bash
# Build the executable
build_scripts\build_windows.bat

# Package it
7z a Hillshade_Converter_Windows.zip dist\hillshade_converter.exe
```

Or on macOS:
```bash
zip -r Hillshade_Converter_Windows.zip dist/hillshade_converter.exe
```

## Publishing to GitHub Releases

### Using GitHub CLI (recommended)

```bash
# Install if needed: brew install gh
gh login

# Create a release
gh release create v1.0.0 \
  Hillshade_Converter_macOS_arm64.tar.gz \
  Hillshade_Converter_macOS_x86_64.tar.gz \
  Hillshade_Converter_Windows.zip \
  --title "Version 1.0.0" \
  --notes "Initial release of Hillshade Converter"
```

### Using Website

1. Go to https://github.com/YOUR_USERNAME/hillshade-converter/releases
2. Click "Create a new release"
3. Tag version: `v1.0.0`
4. Title: `Version 1.0.0`
5. Description: (see template below)
6. Upload the .tar.gz and .zip files
7. Publish

#### Release Description Template

```
## Hillshade Converter v1.0.0

Convert GeoTIFF DEM files to offline MBTiles hillshade tiles.

### Features
- Real-time preview with adjustable parameters
- Configurable shading (Z-factor, azimuth, altitude)
- Support for custom zoom levels
- Code-signed macOS builds

### Installation
- **macOS**: Download, extract, move to Applications
- **Windows**: Download, extract, run exe

### Requirements
- GDAL (macOS: `brew install gdal`, Windows: GIS Internals)

### Downloads
- `Hillshade_Converter_macOS_arm64.tar.gz` - Apple Silicon (M1/M2/M3)
- `Hillshade_Converter_macOS_x86_64.tar.gz` - Intel Mac
- `Hillshade_Converter_Windows.zip` - Windows 10/11

See [README.md](https://github.com/YOUR_USERNAME/hillshade-converter) for detailed usage.
```

## Adding to pagetech.co.uk

1. Copy the contents of `website_snippet.html` into your website
2. Update the version numbers in download links (e.g., `v1.0.0`)
3. Ensure links point to your GitHub releases

Quick way to get download links:
```
https://github.com/YOUR_USERNAME/hillshade-converter/releases/download/v1.0.0/FILENAME
```

## Automatic Updates (Optional)

You can create a simple `version.json` file in your repo for auto-update checking:

```json
{
  "latest": "1.0.0",
  "downloadUrl": "https://github.com/pagetech/hillshade-converter/releases/download/v1.0.0/",
  "platforms": {
    "macos-arm64": "Hillshade_Converter_macOS_arm64.tar.gz",
    "macos-x86": "Hillshade_Converter_macOS_x86_64.tar.gz",
    "windows": "Hillshade_Converter_Windows.zip"
  }
}
```

## Notarization (macOS, Recommended)

For macOS 11+, notarization is strongly recommended. Use the automated script:

```bash
./build_scripts/notarize_mac.sh
```

Or manually:

```bash
# Create a zip of the signed app
ditto -c -k --sequesterRsrc --keepParent \
  "dist/Hillshade Converter.app" \
  Hillshade_Converter_macOS_arm64.zip

# Submit for notarization (requires stored credentials)
xcrun notarytool submit Hillshade_Converter_macOS_arm64.zip \
  --keychain-profile "pagetech-notary" \
  --wait

# Staple the notarization ticket
xcrun stapler staple "dist/Hillshade Converter.app"

# Verify
spctl -a -vv "dist/Hillshade Converter.app"
```

## Troubleshooting

### macOS: "App is damaged and cannot be opened"
- Run: `xattr -d com.apple.quarantine "dist/Hillshade Converter.app"`
- Or disable Gatekeeper (not recommended): `sudo spctl --master-disable`

### Code signing fails
- List available certs: `security find-certificate -c "Developer ID"`
- Verify cert is in your default keychain
- Try with full path: `/usr/bin/codesign ...`

### Windows: "App cannot be found"
- Ensure Python 3 is installed and accessible
- Run from a terminal to see detailed error messages

### Missing GDAL
- macOS: Install with Homebrew: `brew install gdal`
- Windows: Download from GIS Internals and add to PATH

## Summary

**Your distribution workflow:**
1. Make changes → Commit to GitHub
2. Create release tags (`v1.0.0`)
3. Run build scripts (`./build_scripts/build_mac.sh`)
4. Sign macOS builds (`./build_scripts/sign_mac.sh`)
5. Notarize macOS builds (`./build_scripts/notarize_mac.sh`)
6. Package releases (`.tar.gz` or `.zip`)
7. Upload to GitHub Releases
8. Update downloads on pagetech.co.uk
9. Share releases!

Notarization ensures users can download and run your app without any macOS security warnings.
