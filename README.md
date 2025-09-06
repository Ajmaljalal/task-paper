# 📝 TaskPaper

A macOS menu bar app that generates dynamic wallpapers based on your calendar events with AI-powered task triaging.

![TaskPaper Icon](https://img.shields.io/badge/macOS-10.14+-blue?style=flat-square&logo=apple)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## ✨ Features

- 🎨 **Dynamic Wallpapers** - Automatically generates beautiful wallpapers based on your calendar events
- �� **AI Task Triaging** - Uses OpenAI GPT-4 to intelligently identify urgent tasks from calendar events
- 🎤 **Voice Recording** - Capture voice memos for tasks directly from the menu bar
- 📅 **Google Calendar Integration** - Seamlessly syncs with your Google Calendar
- 🔄 **Auto-Updates** - Refreshes wallpaper every 60 seconds with latest calendar data
- 📝 **Menu Bar Interface** - Clean, minimal interface that stays out of your way
- ⚙️ **Easy Configuration** - Simple setup through intuitive settings window

## 📥 Download

**[Download Latest Release](https://github.com/Ajmaljalal/task-paper/releases/latest)**

### Installation Options:
- **TaskPaper-v1.0.0.dmg** (49MB) - **Recommended** - Professional installer
- **TaskPaper-v1.0.0.zip** (121MB) - Direct app bundle

## 🚀 Quick Start

### 1. Installation
- **DMG**: Double-click → Drag to Applications
- **ZIP**: Unzip → Drag to Applications

### 2. First Launch
1. Launch TaskPaper from Applications
2. Look for the 📝 icon in your menu bar
3. Enter your OpenAI API key when prompted
4. Connect your Google Calendar (Menu → "Connect Google…")
5. Grant calendar and notification permissions

### 3. Enjoy!
Your wallpaper will now automatically update with urgent tasks from your calendar!

## 📋 Requirements

- **macOS**: 10.14 (Mojave) or later
- **Architecture**: Universal (Intel & Apple Silicon)
- **OpenAI API Key**: Required for AI features ([Get yours here](https://platform.openai.com/api-keys))
- **Google Calendar**: Optional but recommended

## 🎯 How It Works

1. **Calendar Sync**: Connects to your Google Calendar to fetch today's events
2. **AI Analysis**: Uses OpenAI GPT-4 to analyze events and identify urgent, actionable tasks
3. **Wallpaper Generation**: Creates a beautiful wallpaper displaying your most important tasks
4. **Auto-Refresh**: Updates every 60 seconds to keep information current
5. **Menu Bar Control**: Manage everything from the convenient menu bar interface

## 🛠️ Menu Bar Options

- **📝** - TaskPaper icon (click for menu)
- **Add Task** - Record voice memos for future task capture
- **Connect Google…** - Set up Google Calendar integration
- **Settings…** - Configure OpenAI API key and preferences
- **Pause/Resume** - Control automatic wallpaper updates
- **Refresh Now** - Force immediate wallpaper update

## ⚙️ Configuration

### OpenAI API Key
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click the 📝 menu bar icon → "Settings…"
3. Enter your API key and click "Save"
4. The key is stored securely in: `~/Library/Application Support/TaskPaper/config.json`

### Google Calendar
1. Click the 📝 menu bar icon → "Connect Google…"
2. Follow the OAuth flow to grant calendar access
3. Credentials are stored in: `~/Library/Application Support/TaskPaper/token.json`

## 🔧 Development

### Prerequisites
- Python 3.10+
- macOS development environment

### Setup
```bash
# Clone the repository
git clone https://github.com/Ajmaljalal/task-paper.git
cd task-paper

# Create virtual environment
python -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

### Building

#### Quick Development Build
```bash
./quick_build.sh
```

#### Complete Release Build
```bash
./build_and_package.sh
```

This creates:
- `dist/TaskPaper.app` - The application bundle
- `release/TaskPaper-v1.0.0.dmg` - Professional installer
- `release/TaskPaper-v1.0.0.zip` - Direct app bundle
- `release/RELEASE_NOTES.md` - Release documentation

### Project Structure
```
task-paper/
├── main.py                 # Application entry point
├── settings.py             # Settings window and OpenAI config
├── voice_window.py         # Voice recording interface
├── config_window.py        # Configuration window wrapper
├── config.py               # App configuration and constants
├── auth.py                 # Google OAuth handling
├── calendar_service.py     # Google Calendar API integration
├── triage.py               # AI-powered task triaging
├── renderer.py             # Wallpaper generation
├── wallpaper_manager.py    # macOS wallpaper management
├── voice_recorder.py       # Voice recording functionality
├── models.py               # Data models
├── TaskPaper.spec          # PyInstaller configuration
├── requirements.txt        # Python dependencies
├── build_and_package.sh    # Complete build script
└── quick_build.sh          # Development build script
```

## 🔐 Privacy & Security

- **Local Storage**: All data is stored locally on your Mac
- **API Keys**: OpenAI API key stored securely in macOS Application Support
- **Google Auth**: Uses OAuth 2.0 with minimal required permissions
- **No Telemetry**: No usage data is collected or transmitted
- **Open Source**: Full source code available for audit

## 🐛 Troubleshooting

### Common Issues

**"App is damaged" Error**
```bash
# Right-click the app and select "Open" (first time only)
# Or remove quarantine attribute:
xattr -cr /Applications/TaskPaper.app
```

**No Wallpaper Updates**
- Check Google Calendar connection in menu
- Verify calendar permissions in System Preferences
- Try "Refresh Now" from menu

**AI Features Not Working**
- Verify OpenAI API key in Settings
- Check API key has sufficient credits
- Ensure internet connection

**Voice Recording Issues**
- Grant microphone permissions in System Preferences
- Install audio dependencies: `pip install sounddevice numpy`

### Reset Configuration
```bash
# Remove all app data (will require re-setup)
rm -rf ~/Library/Application\ Support/TaskPaper/
```

## 📊 System Integration

### Wallpaper Management
- Automatically sets wallpaper on all displays
- Keeps last 3 wallpapers for cleanup
- Generates high-resolution images for Retina displays

### Voice Recordings
- Saved to: `~/Library/Application Support/TaskPaper/voice_recordings/`
- WAV format at CD quality (44.1kHz)
- Automatic cleanup keeps last 10 recordings

### Background Operation
- Runs as LSUIElement (no dock icon)
- Minimal CPU usage when idle
- Smart refresh scheduling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and small

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **rumps** - For the excellent macOS menu bar framework
- **OpenAI** - For powerful AI capabilities
- **Google Calendar API** - For seamless calendar integration
- **Pillow** - For image processing and wallpaper generation
- **PyInstaller** - For creating standalone macOS applications

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Ajmaljalal/task-paper/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/Ajmaljalal/task-paper/issues) with `enhancement` label
- **Discussions**: [GitHub Discussions](https://github.com/Ajmaljalal/task-paper/discussions)

---

**Made with ❤️ for productivity enthusiasts**

*TaskPaper helps you stay focused on what matters most by intelligently surfacing urgent tasks from your calendar right on your desktop.*
