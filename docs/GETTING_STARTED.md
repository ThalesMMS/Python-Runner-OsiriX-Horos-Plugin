# Getting Started with Python Runner Plugin

**Time to complete:** ~5 minutes

This guide will walk you through installing and running your first Python script in Horos/OsiriX. By the end, you'll have a working plugin that executes Python code directly from your medical imaging software.

---

## Prerequisites

Before you begin, verify you have everything needed:

### 1. Check your macOS version

```bash
sw_vers
```

**Expected output:**
```
ProductName:    macOS
ProductVersion: 11.0 (or later)
```

✅ **Required:** macOS 11.0 or later

### 2. Check Python installation

```bash
python3 --version
```

**Expected output:**
```
Python 3.x.x
```

✅ **Required:** Python 3 available via `python3` command

### 3. Check Xcode installation (for building)

```bash
xcodebuild -version
```

**Expected output:**
```
Xcode 15.x or 16.x
Build version xxxxx
```

✅ **Required:** Xcode 15 or later

### 4. Verify your platform

You need either:
- **Horos** 4.0 or later, OR
- **OsiriX MD** 12.0 or later

**Note for Apple Silicon users (M1/M2/M3):** ✅ Fully supported! No special configuration needed.

---

## Step 1: Get the Code

Clone the repository to your local machine:

```bash
cd ~/Documents
git clone https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin.git
cd Python-Runner-OsiriX-Horos-Plugin
```

**Expected output:**
```
Cloning into 'Python-Runner-OsiriX-Horos-Plugin'...
remote: Enumerating objects: xxx, done.
remote: Counting objects: 100% (xxx/xxx), done.
```

✅ **Verify:** Run `ls` and you should see:
- `build.sh`
- `Python-Runner-Horos-Plugin/`
- `README.md`
- `Releases/`

---

## Step 2: Build the Plugin

Build the plugin for your platform using the automated build script:

### For Horos users:

```bash
./build.sh horos
```

### For OsiriX users:

```bash
./build.sh osirix
```

**Expected output:**
```
========================================
Building for Horos...
========================================
Copying Horos project files...
Building...
BUILD SUCCEEDED
Build successful!
Creating zip...
Plugin copied to: /path/to/Releases/Horos/
Zip created: /path/to/Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip
```

✅ **Verify:** Check that the zip file exists:

```bash
# For Horos
ls -lh Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip

# For OsiriX
ls -lh Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip
```

**Troubleshooting:**
- If build fails with "xcodebuild: error", ensure Xcode is fully installed and command line tools are configured
- Run `xcode-select --install` if needed
- Check Console.app for detailed error messages

---

## Step 3: Install the Plugin

### For Horos:

```bash
# Extract to Horos plugins directory
unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip \
  -d "$HOME/Library/Application Support/Horos/Plugins/"

# Sign the plugin (required on modern macOS)
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

### For OsiriX:

```bash
# Extract to OsiriX plugins directory
unzip -o Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip \
  -d "$HOME/Library/Application Support/OsiriX/Plugins/"

# Sign the plugin (required on modern macOS)
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Expected output:**
```
Archive:  Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip
   creating: /Users/yourname/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/
   ...
PythonRunnerHorosPlugin.osirixplugin: replacing existing signature
```

✅ **Verify:** Check the plugin was installed:

```bash
# For Horos
ls -d "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# For OsiriX
ls -d "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

---

## Step 4: Restart Horos/OsiriX

**Important:** You must restart the application for the plugin to load.

1. Quit Horos/OsiriX completely (⌘Q)
2. Relaunch the application
3. Wait for it to fully start

---

## Step 5: Verify Plugin Installation

Check that the plugin loaded successfully:

1. In Horos/OsiriX, go to `Plugins > Plugin Manager`
2. Look for **PythonRunnerHorosPlugin** in the list
3. It should show as "Loaded" or "Active"

**Troubleshooting:**
- If the plugin doesn't appear, check Console.app (search for "Horos" or "OsiriX")
- Look for error messages about plugin loading
- Ensure the plugin was properly signed (Step 3)

---

## Step 6: Run Your First Python Script

Now for the exciting part - running Python code from Horos/OsiriX!

### Prepare the environment:

1. Open any study in Horos/OsiriX
2. Open a 2D viewer window (double-click a series)
3. **Important:** Ensure the 2D viewer window is active (in front)

   > **Why?** Image Filter plugins are only enabled when a viewer window is active.

### Execute the script:

Go to the menu: **Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script**

### Expected output:

**Console output** (open Console.app and filter for your app):
```
Executing Python script: main.py
Hello world
Python script executed successfully
```

**Alert dialog:**
You should see a dialog box appear with the message: **"Hello world"**

Click **OK** to dismiss it.

---

## Step 7: Understanding What Happened

Let's examine the Python script that just ran:

```bash
cat Python-Runner-Horos-Plugin/python_script/main.py
```

**You should see:**
```python
#!/usr/bin/env python3

def main():
    print("Hello world")

if __name__ == "__main__":
    main()
```

**What happened:**
1. You selected "Run Python Script" from the plugin menu
2. The plugin located `python_script/main.py` inside the plugin bundle
3. It executed the script using `python3`
4. The script printed "Hello world" to the console
5. The plugin showed an alert with the message

---

## Next Steps

🎉 **Congratulations!** You now have a working Python-integrated Horos/OsiriX plugin.

### Customize the Python script

Edit the Python script to do something more interesting:

1. Navigate to the plugin in Finder:
   ```bash
   # For Horos
   open "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

   # For OsiriX
   open "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
   ```

2. Right-click the plugin bundle > "Show Package Contents"
3. Navigate to `Contents/Resources/python_script/main.py`
4. Edit `main.py` with your own Python code
5. Save and run "Run Python Script" again

### Example modifications:

**Try this** - Replace `main.py` content with:

```python
#!/usr/bin/env python3

import sys
from datetime import datetime

def main():
    print(f"Script executed at: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")

if __name__ == "__main__":
    main()
```

Run the plugin again and check the console output!

### Learn more

- **Add Python dependencies:** Learn how to bundle pip packages with your plugin
- **Access DICOM data:** Explore how to pass DICOM information to Python scripts
- **Create complex workflows:** Build multi-step image processing pipelines
- **Customize the UI:** Add configuration dialogs and user preferences

See the full [README.md](../README.md) for advanced topics and architecture details.

---

## Troubleshooting

### Plugin doesn't appear in menu

1. Check Plugin Manager to verify it loaded
2. Ensure a 2D viewer window is active (Image Filters require this)
3. Check Console.app for error messages
4. Verify the plugin was signed: `codesign -dv "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"`

### Python script doesn't run

1. Verify Python 3 is installed: `python3 --version`
2. Check Console.app for Python errors
3. Ensure `main.py` has correct permissions: `chmod +x main.py`
4. Test the script directly: `python3 Python-Runner-Horos-Plugin/python_script/main.py`

### Build fails

1. Ensure Xcode is fully installed (not just command line tools)
2. Check you have accepted Xcode license: `sudo xcodebuild -license accept`
3. Verify command line tools are configured: `xcode-select -p`
4. Try cleaning first: `xcodebuild clean` before building

### Permission errors on Apple Silicon

Code signing is required on Apple Silicon and modern macOS. Always run:
```bash
codesign --force --deep --sign - "path/to/plugin"
```

---

## Quick Reference

### Build commands
```bash
./build.sh horos    # Build for Horos
./build.sh osirix   # Build for OsiriX
./build.sh both     # Build for both platforms
```

### Install locations
```bash
# Horos plugins
~/Library/Application Support/Horos/Plugins/

# OsiriX plugins
~/Library/Application Support/OsiriX/Plugins/
```

### Plugin menu path
```
Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script
```

### Key files
```
PythonRunnerHorosPlugin.osirixplugin/
└── Contents/
    ├── Resources/
    │   └── python_script/
    │       └── main.py          # Your Python script
    └── MacOS/
        └── PythonRunnerHorosPlugin  # Plugin binary
```

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin/issues)
- **Documentation:** [README.md](../README.md)
- **Examples:** Check the `python_script/` directory for sample scripts

**Ready to build something amazing?** Start editing `main.py` and unleash the power of Python in your medical imaging workflow!
