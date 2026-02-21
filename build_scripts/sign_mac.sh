#!/bin/bash
# Code signing script for macOS
# Signs the built application with your Apple Developer certificate
# Usage: ./build_scripts/sign_mac.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

APP_PATH="dist/Hillshade Converter.app"
TEAM_ID="YOUR_TEAM_ID"  # Change this to your Apple Team ID

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App not found at $APP_PATH"
    echo "Please run ./build_scripts/build_mac.sh first"
    exit 1
fi

echo "🔐 Code Signing Hillshade Converter for macOS..."
echo ""

# Find available certificates
echo "Available Developer ID Certificates:"
security find-identity -v -p codesigning | grep "Developer ID Application" || true
echo ""

# Prompt for certificate name
read -p "Enter the exact certificate name (e.g., 'Developer ID Application: Your Name (TEAMID)'): " CERT_NAME

if [ -z "$CERT_NAME" ]; then
    echo "❌ No certificate name provided"
    exit 1
fi

# Sign the entire app bundle
echo "Signing app with certificate: $CERT_NAME"
codesign --force --deep --strict --options=runtime --timestamp --entitlements entitlements.plist --sign "$CERT_NAME" "$APP_PATH"

# Verify signature
echo ""
echo "✅ Signing complete!"
echo ""
echo "Verifying signature..."
codesign -v "$APP_PATH"

echo ""
echo "Signature details:"
codesign -d --verbose=4 "$APP_PATH" 2>&1 | head -30

echo ""
echo "Gatekeeper assessment:"
spctl -a -vv "$APP_PATH" || true
