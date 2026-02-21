#!/bin/bash
# Notarization script for macOS
# Notarizes the signed application with Apple
# Usage: ./build_scripts/notarize_mac.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

APP_PATH="dist/Hillshade Converter.app"
ZIP_NAME="Hillshade_Converter_macOS_arm64.zip"
KEYCHAIN_PROFILE="pagetech-notary"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App not found at $APP_PATH"
    echo "Please run ./build_scripts/build_mac.sh first"
    exit 1
fi

echo "📝 Notarizing Hillshade Converter for macOS..."
echo ""

# Check if app is signed
echo "Checking code signature..."
if ! codesign -dvv "$APP_PATH" 2>&1 | grep -q "Developer ID Application"; then
    echo "❌ App is not signed with Developer ID Application certificate"
    echo "Please run ./build_scripts/sign_mac.sh first"
    exit 1
fi

echo "✅ App is properly signed"
echo ""

# Create zip for notarization
echo "📦 Creating archive for notarization..."
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
fi
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_NAME"

echo "✅ Archive created: $ZIP_NAME"
echo ""

# Submit for notarization
echo "🚀 Submitting to Apple for notarization..."
echo "This may take a few minutes..."
echo ""

if ! xcrun notarytool submit "$ZIP_NAME" --keychain-profile "$KEYCHAIN_PROFILE" --wait; then
    echo ""
    echo "❌ Notarization failed!"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure keychain profile exists:"
    echo "     xcrun notarytool store-credentials \"$KEYCHAIN_PROFILE\" \\"
    echo "       --apple-id \"your@email.com\" \\"
    echo "       --team-id \"YOUR_TEAM_ID\" \\"
    echo "       --password \"xxxx-xxxx-xxxx-xxxx\""
    echo ""
    echo "  2. Get app-specific password from: https://appleid.apple.com"
    echo ""
    echo "  3. Check submission history:"
    echo "     xcrun notarytool history --keychain-profile \"$KEYCHAIN_PROFILE\""
    exit 1
fi

echo ""
echo "✅ Notarization approved!"
echo ""

# Staple the notarization ticket
echo "📌 Stapling notarization ticket to app..."
xcrun stapler staple "$APP_PATH"

echo "✅ Ticket stapled successfully!"
echo ""

# Verify Gatekeeper acceptance
echo "🔍 Verifying Gatekeeper assessment..."
if spctl -a -vv "$APP_PATH" 2>&1 | grep -q "accepted"; then
    echo "✅ App will be accepted by Gatekeeper!"
else
    echo "⚠️  Gatekeeper assessment:"
    spctl -a -vv "$APP_PATH" || true
fi

echo ""
echo "🎉 Notarization complete!"
echo ""
echo "Next steps:"
echo "  1. Recreate the release archive (now with stapled ticket):"
echo "     tar -czf Hillshade_Converter_macOS_arm64.tar.gz -C dist \"Hillshade Converter.app\""
echo ""
echo "  2. Upload to GitHub Releases:"
echo "     gh release create v1.0.0 Hillshade_Converter_macOS_arm64.tar.gz"
echo ""
echo "  3. Users can now download and run without warnings!"
