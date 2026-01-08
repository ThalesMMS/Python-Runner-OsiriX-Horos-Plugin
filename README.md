# Python Runner Horos Plugin

Minimal Horos plugin that runs a bundled Python script and shows an alert. It is meant as a clean template you can extend.

---

## Status

Working minimal template. Runs `python_script/main.py`, prints to the Xcode console, and shows a "Hello world" alert.

---

## Overview

- Open a study and make a 2D viewer window active before using the menu item
- Menu item: `Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script`
- Action: runs `python_script/main.py` and prints to the Xcode console
- UI: shows a simple "Hello world" alert in Horos
- No DICOM export/import, no configuration UI

---

## Requirements

- macOS 11+ (tested on Horos 4.x)
- Xcode 15/16+ for building the plugin
- Python 3 available via `python3` in PATH

---

## Quick Build & Install

1. **Build the plugin**
   ```bash
   xcodebuild \
     -project MyOsiriXPluginFolder-Swift/PythonRunnerHorosPlugin.xcodeproj \
     -configuration Release \
     -target PythonRunnerHorosPlugin \
     build
   ```

2. **Install into Horos**
   ```bash
   PLUGIN_SRC="MyOsiriXPluginFolder-Swift/build/Release/PythonRunnerHorosPlugin.osirixplugin"
   PLUGIN_DST="$HOME/Library/Application Support/Horos/Plugins/"

   rm -rf "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
   cp -R "$PLUGIN_SRC" "$PLUGIN_DST"
   codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
   ```

3. **Launch Horos** and confirm the entry under `Plugins > Image Filters > PythonRunnerHorosPlugin`.

---

## Using the Plugin

1. Open a study and bring a 2D viewer window to the front (Image Filters are disabled without an active viewer).
2. Choose `Run Python Script` from the plugin menu.
3. Check the Xcode console for `Hello world` from `python_script/main.py`.
4. A simple alert appears inside Horos.

---

## Repository Layout

```
MyOsiriXPluginFolder-Swift/     # Horos plugin sources
MyOsiriXPluginFolder-Swift/python_script/  # Bundled Python entrypoint
```

---

## License

MIT. See `LICENSE`.
