# Python Runner Horos Plugin

Minimal Horos/OsiriX plugin that runs a bundled Python script and shows an alert. It is meant as a clean template you can extend.

---

## Status

Working minimal template. Runs `python_script/main.py`, prints to the console, and shows a "Hello world" alert.

---

## Overview

- Open a study and make a 2D viewer window active before using the menu item
- Menu item: `Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script`
- Action: runs `python_script/main.py` and prints to the console
- UI: shows a simple "Hello world" alert
- No DICOM export/import, no configuration UI

---

## Requirements

- macOS 11+
- Xcode 15/16+ for building the plugin
- Python 3 available via `python3` in PATH

---

## Quick Build & Install

### Using the build script (recommended)

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

### Manual install

```bash
# For Horos
PLUGIN_DST="$HOME/Library/Application Support/Horos/Plugins/"

# For OsiriX
PLUGIN_DST="$HOME/Library/Application Support/OsiriX/Plugins/"

# Copy and sign
unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"
codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
```

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
