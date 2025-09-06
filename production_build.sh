#!/bin/bash

# TaskPaper - Complete Build and Package Script
# This script builds the app and creates distribution files for GitHub release

set -e  # Exit on any error

VERSION="1.0.0"
APP_NAME="TaskPaper"
RELEASE_DIR="release"

echo "🚀 TaskPaper Complete Build and Package Script v$VERSION"
echo "=================================================="

# Function to print colored output
print_status() {
    echo "📦 $1"
}

print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Attempting to activate..."
    if [[ -f "env/bin/activate" ]]; then
        source env/bin/activate
        echo "✅ Activated virtual environment"
    else
        print_error "No virtual environment found. Please create one with:"
        echo "  python -m venv env"
        echo "  source env/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
fi

# Install/Update PyInstaller
print_status "Installing PyInstaller..."
pip install pyinstaller

# Build the app using PyInstaller
print_status "Building $APP_NAME.app with PyInstaller..."
pyinstaller TaskPaper.spec

# Check if build was successful
if [[ ! -d "dist/$APP_NAME.app" ]]; then
    print_error "Build failed! App not found at dist/$APP_NAME.app"
    exit 1
fi

print_success "App built successfully: dist/$APP_NAME.app"

# Get app size
APP_SIZE=$(du -sh "dist/$APP_NAME.app" | cut -f1)
print_status "App size: $APP_SIZE"

# Create DMG installer
print_status "Creating DMG installer..."
DMG_NAME="$APP_NAME-v$VERSION.dmg"
hdiutil create -volname "$APP_NAME v$VERSION" \
    -srcfolder "dist/$APP_NAME.app" \
    -ov -format UDZO \
    "$RELEASE_DIR/$DMG_NAME"

if [[ ! -f "$RELEASE_DIR/$DMG_NAME" ]]; then
    print_error "DMG creation failed!"
    exit 1
fi

print_success "DMG created: $RELEASE_DIR/$DMG_NAME"

# Create ZIP archive
print_status "Creating ZIP archive..."
ZIP_NAME="$APP_NAME-v$VERSION.zip"
cd dist
zip -r "../$RELEASE_DIR/$ZIP_NAME" "$APP_NAME.app"
cd ..

if [[ ! -f "$RELEASE_DIR/$ZIP_NAME" ]]; then
    print_error "ZIP creation failed!"
    exit 1
fi

print_success "ZIP created: $RELEASE_DIR/$ZIP_NAME"

# Get file sizes
DMG_SIZE=$(du -h "$RELEASE_DIR/$DMG_NAME" | cut -f1)
ZIP_SIZE=$(du -h "$RELEASE_DIR/$ZIP_NAME" | cut -f1)

# Create release notes
print_status "Generating release notes..."
cat > "$RELEASE_DIR/RELEASE_NOTES.md" << NOTES
# 📝 $APP_NAME v$VERSION

## ✨ Features
- 🎨 **Dynamic Wallpapers** - Auto-generates wallpapers based on calendar events
- 🤖 **AI Task Triaging** - Uses OpenAI to identify urgent tasks from calendar
- 🎤 **Voice Recording** - Capture voice memos for tasks
- 📅 **Google Calendar Integration** - Syncs with your Google Calendar
- 🔧 **Easy Setup** - Simple configuration through menu bar with 📝 icon

## 📥 Download Options
- **$DMG_NAME** ($DMG_SIZE) - **Recommended installer**
- **$ZIP_NAME** ($ZIP_SIZE) - Direct app bundle

## 🚀 Installation
### Using DMG (Recommended):
1. Download the DMG file
2. Double-click to open
3. Drag $APP_NAME.app to Applications folder
4. Launch from Applications or Spotlight

### Using ZIP:
1. Download and unzip the file
2. Drag $APP_NAME.app to Applications folder
3. Launch from Applications

## ⚙️ First-Time Setup
1. **OpenAI API Key**: App will prompt for API key on first launch
   - Get your key from: https://platform.openai.com/api-keys
   - Required for AI-powered task triaging
2. **Google Calendar**: Connect via menu → "Connect Google…"
3. **Permissions**: Grant calendar and notification permissions when prompted

## 📋 System Requirements
- **macOS**: 10.14 (Mojave) or later
- **Architecture**: Universal (Intel & Apple Silicon)
- **Dependencies**: Self-contained (no Python installation required)

## 🎯 How It Works
1. Connects to your Google Calendar
2. Uses AI to analyze upcoming events and deadlines
3. Generates a beautiful wallpaper with urgent tasks
4. Updates automatically every 60 seconds
5. Runs quietly in the menu bar

## 🛠️ Menu Bar Options
- **Add Task** - Record voice memos
- **Connect Google…** - Set up calendar integration  
- **Settings…** - Configure OpenAI API key
- **Pause/Resume** - Control wallpaper updates
- **Refresh Now** - Force immediate update

## 🐛 Troubleshooting
- **"App is damaged"**: Right-click → Open (first time only)
- **No wallpaper updates**: Check Google Calendar connection
- **AI not working**: Verify OpenAI API key in Settings
- **Permission issues**: Check System Preferences → Security & Privacy

## 📞 Support
- **Issues**: Report at GitHub repository
- **Feature requests**: Create an issue with enhancement label
- **Documentation**: Check README.md

---
**Note**: This app stores your OpenAI API key locally in:
\`~/Library/Application Support/$APP_NAME/config.json\`
NOTES

# Create installation guide
print_status "Creating installation guide..."
cat > "$RELEASE_DIR/INSTALLATION.md" << INSTALL
# 📱 TaskPaper Installation Guide

## Quick Install (DMG - Recommended)
1. Download \`$DMG_NAME\`
2. Double-click the DMG file
3. Drag TaskPaper.app to Applications folder
4. Launch TaskPaper from Applications

## Alternative Install (ZIP)
1. Download \`$ZIP_NAME\`
2. Unzip the file
3. Drag TaskPaper.app to Applications folder
4. Launch TaskPaper from Applications

## First Launch Setup
1. **Security Prompt**: If you see "App is damaged", right-click and select "Open"
2. **OpenAI Setup**: Enter your API key when prompted
3. **Calendar Connection**: Click "Connect Google…" in the menu
4. **Permissions**: Grant calendar and notification access

## Verification
- Look for the 📝 icon in your menu bar
- Check that wallpaper updates with calendar events
- Test voice recording with "Add Task" menu option

## Uninstall
To remove TaskPaper:
1. Drag TaskPaper.app to Trash
2. Delete settings: \`~/Library/Application Support/TaskPaper/\`
INSTALL

# Summary
echo ""
echo "🎉 BUILD AND PACKAGE COMPLETE!"
echo "================================"
echo ""
echo "📁 Release files created in: $RELEASE_DIR/"
echo ""
echo "📦 Distribution Files:"
echo "  • $DMG_NAME ($DMG_SIZE) - Installer"
echo "  • $ZIP_NAME ($ZIP_SIZE) - App bundle"
echo "  • RELEASE_NOTES.md - GitHub release notes"
echo "  • INSTALLATION.md - User installation guide"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test the app: open dist/$APP_NAME.app"
echo "  2. Create GitHub repository (if needed)"
echo "  3. Create GitHub release with tag v$VERSION"
echo "  4. Upload both DMG and ZIP files"
echo "  5. Copy release notes from RELEASE_NOTES.md"
echo ""
echo "📋 Quick Test Commands:"
echo "  • Test DMG: open $RELEASE_DIR/$DMG_NAME"
echo "  • Test APP: open dist/$APP_NAME.app"
echo "  • View files: ls -lh $RELEASE_DIR/"
echo ""
print_success "Ready for distribution! 🚀"
