# 📝 TaskPaper v1.0.0

## ✨ Features
- 🎨 **Dynamic Wallpapers** - Auto-generates wallpapers based on calendar events
- 🤖 **AI Task Triaging** - Uses OpenAI to identify urgent tasks from calendar
- 🎤 **Voice Recording** - Capture voice memos for tasks
- 📅 **Google Calendar Integration** - Syncs with your Google Calendar
- 🔧 **Easy Setup** - Simple configuration through menu bar with 📝 icon

## 📥 Download Options
- **TaskPaper-v1.0.0.dmg** ( 52M) - **Recommended installer**
- **TaskPaper-v1.0.0.zip** (112M) - Direct app bundle

## 🚀 Installation
### Using DMG (Recommended):
1. Download the DMG file
2. Double-click to open
3. Drag TaskPaper.app to Applications folder
4. Launch from Applications or Spotlight

### Using ZIP:
1. Download and unzip the file
2. Drag TaskPaper.app to Applications folder
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
`~/Library/Application Support/TaskPaper/config.json`
