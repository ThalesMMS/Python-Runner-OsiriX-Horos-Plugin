# Python Runner OsiriX/Horos Plugin

A minimal template for building Horos/OsiriX plugins with Python integration. This plugin demonstrates the workflow for running Python scripts from within medical imaging software, with support for both Horos and OsiriX platforms.

---

## Status

- **Working minimal template** - Starting point for building custom plugins.

Runs `python_script/main.py`, prints to the console, and shows a "Hello world" alert.

---

## Overview

This plugin provides:

- **Python Integration**: Execute Python scripts directly from Horos/OsiriX
- **Dual-Platform Support**: Single codebase for both Horos and OsiriX
- **Clean Template**: Minimal working example you can extend
- **Simple Workflow**: Menu item → Python script → Console output → Alert

### What it does

- Open a study and make a 2D viewer window active before using the menu item
- Menu item: `Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script`
- Action: runs `python_script/main.py` and prints to the console
- UI: shows a simple "Hello world" alert
- No DICOM export/import, no configuration UI

---

## Quick Start Guide

Get up and running:

### 1. Build the plugin

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin.git
cd Python-Runner-OsiriX-Horos-Plugin

# Build for your platform
./build.sh horos    # For Horos users
./build.sh osirix   # For OsiriX users
```

### 2. Install the plugin

```bash
# For Horos
unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip -d "$HOME/Library/Application Support/Horos/Plugins/"
codesign --force --deep --sign - "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# For OsiriX
unzip -o Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip -d "$HOME/Library/Application Support/OsiriX/Plugins/"
codesign --force --deep --sign - "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

### 3. Restart and test

1. Restart Horos/OsiriX
2. Open any study and bring a 2D viewer window to the front
3. Go to `Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script`
4. You should see "Hello world" in the console and an alert dialog

**Complete.** You now have a working plugin. Modify `python_script/main.py` to add your own functionality.

---

## Requirements

- **macOS**: 11.0 or later
- **Xcode**: 15 or 16+ for building the plugin
- **Python**: Python 3 available via `python3` in PATH
- **Apple Silicon**: Supported on M1/M2/M3 Macs
  - Both Rosetta and native arm64 builds supported
  - No special configuration needed
  - Same build process for Intel and Apple Silicon

### Platform-Specific Requirements

- **For Horos**: Horos 4.0 or later recommended
- **For OsiriX**: OsiriX MD 12.0 or later recommended

---

## Detailed Installation

### Building the Plugin

#### Using the build script (recommended)

The automated build script handles all configuration switching and compilation:

```bash
# Build for Horos only
./build.sh horos

# Build for OsiriX only
./build.sh osirix

# Build for both platforms
./build.sh both
```

Built plugins are placed in:
- `Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip`
- `Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip`

The build script automatically:
- Switches between platform-specific Xcode configurations
- Builds the plugin with the correct framework
- Archives and zips the plugin for distribution

#### Manual Xcode build

If you prefer to build manually in Xcode:

1. Open `PythonRunnerHorosPlugin.xcodeproj`
2. Ensure the correct platform configuration is active (see `build.sh` for details)
3. Build the project (⌘B)
4. The plugin will be in the build output directory

### Installing the Plugin

#### For Horos

```bash
# Set the Horos plugins directory
PLUGIN_DST="$HOME/Library/Application Support/Horos/Plugins/"

# Extract the plugin
unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"

# Sign the plugin (required on Apple Silicon and modern macOS)
codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
```

#### For OsiriX

```bash
# Set the OsiriX plugins directory
PLUGIN_DST="$HOME/Library/Application Support/OsiriX/Plugins/"

# Extract the plugin
unzip -o Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"

# Sign the plugin (required on Apple Silicon and modern macOS)
codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
```

#### Post-Installation

1. **Restart Horos/OsiriX** - The application must be restarted to load the new plugin
2. **Verify Installation** - Check `Plugins > Plugin Manager` to confirm the plugin loaded
3. **Check Console** - If the plugin doesn't appear, check Console.app for error messages

---

## Using the Plugin

1. Open a study and bring a 2D viewer window to the front (Image Filters are disabled without an active viewer).
2. Choose `Run Python Script` from the plugin menu.
3. Check the console for `Hello world` from `python_script/main.py`.
4. A simple alert appears inside Horos/OsiriX.

---

## Repository Layout

```
Python-Runner-Horos-Plugin/
├── build.sh                              # Build script for both platforms
├── Releases/
│   ├── Horos/                            # Horos build output
│   └── OsiriX/                           # OsiriX build output
└── Python-Runner-Horos-Plugin/           # Plugin sources
    ├── Plugin.swift                      # Main plugin code
    ├── Info.plist                        # Plugin metadata
    ├── python_script/                    # Bundled Python entrypoint
    │   └── main.py
    ├── Horos.framework/                  # Horos SDK
    ├── OsiriXAPI.framework/              # OsiriX SDK
    └── PythonRunnerHorosPlugin.xcodeproj/
        ├── project.pbxproj               # Active project config
        ├── project_Horos.pbxproj         # Horos-specific config
        └── project_OsiriX.pbxproj        # OsiriX-specific config
```

---

## Dual-Platform Architecture

The plugin supports both Horos and OsiriX through platform-specific configuration files:

- `project_Horos.pbxproj` / `project_OsiriX.pbxproj` - Xcode project configs
- `*-Bridging-Header_Horos.h` / `*-Bridging-Header_OsiriX.h` - Swift bridging headers

The `build.sh` script automatically switches between configurations before building.

---

## License

MIT. See `LICENSE`.
