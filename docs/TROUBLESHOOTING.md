# Troubleshooting Guide

This guide covers common issues you may encounter when building, installing, or running the Python Runner plugin for Horos/OsiriX.

**Quick navigation:**
- [Installation Issues](#installation-issues)
- [Plugin Not Loading](#plugin-not-loading)
- [Python Errors](#python-errors)
- [Codesigning Issues](#codesigning-issues)
- [Virtual Environment Problems](#virtual-environment-problems)
- [Apple Silicon Issues](#apple-silicon-issues)
- [Build Failures](#build-failures)
- [Getting Help](#getting-help)

---

## Installation Issues

### Plugin doesn't appear in plugins directory after extraction

**Symptoms:**
- Unzip command succeeds but plugin is not in the expected directory
- Plugin bundle not visible in Finder

**Solution:**

1. Verify the extraction command syntax:
   ```bash
   # For Horos
   unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip \
     -d "$HOME/Library/Application Support/Horos/Plugins/"

   # For OsiriX
   unzip -o Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip \
     -d "$HOME/Library/Application Support/OsiriX/Plugins/"
   ```

2. Check if the plugins directory exists:
   ```bash
   # For Horos
   ls -la "$HOME/Library/Application Support/Horos/Plugins/"

   # For OsiriX
   ls -la "$HOME/Library/Application Support/OsiriX/Plugins/"
   ```

3. If the directory doesn't exist, create it:
   ```bash
   # For Horos
   mkdir -p "$HOME/Library/Application Support/Horos/Plugins/"

   # For OsiriX
   mkdir -p "$HOME/Library/Application Support/OsiriX/Plugins/"
   ```

4. Re-run the unzip command.

### Wrong plugin installed for your platform

**Symptoms:**
- Plugin appears in Plugin Manager but shows as "Incompatible"
- Plugin loads but crashes immediately

**Solution:**

Ensure you built and installed the correct version for your platform:

1. Remove the incorrect plugin:
   ```bash
   # For Horos
   rm -rf "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

   # For OsiriX
   rm -rf "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
   ```

2. Build for the correct platform:
   ```bash
   ./build.sh horos    # For Horos
   ./build.sh osirix   # For OsiriX
   ```

3. Install the correct version (see commands in first issue).

### Permission errors during installation

**Symptoms:**
- "Permission denied" errors when unzipping
- Cannot write to plugins directory

**Solution:**

1. Check directory permissions:
   ```bash
   ls -la "$HOME/Library/Application Support/Horos/"
   ```

2. Fix permissions if needed:
   ```bash
   # For Horos
   chmod 755 "$HOME/Library/Application Support/Horos/Plugins/"

   # For OsiriX
   chmod 755 "$HOME/Library/Application Support/OsiriX/Plugins/"
   ```

3. If the directory is owned by root, reclaim ownership:
   ```bash
   sudo chown -R $(whoami) "$HOME/Library/Application Support/Horos/Plugins/"
   ```

---

## Plugin Not Loading

### Plugin doesn't appear in Plugin Manager

**Symptoms:**
- After restart, plugin is not listed in Plugin Manager
- Menu item not visible under Image Filters

**Diagnostic steps:**

1. **Verify plugin exists:**
   ```bash
   # For Horos
   ls -la "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

   # For OsiriX
   ls -la "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
   ```

2. **Check Console.app for errors:**
   - Open Console.app (Applications > Utilities > Console)
   - In the search bar, type: `Horos` or `OsiriX` or `PythonRunner`
   - Look for plugin loading errors
   - Common error patterns:
     - `Code signature invalid`
     - `Library not loaded`
     - `Incompatible plugin version`

3. **Verify plugin Info.plist:**
   ```bash
   # For Horos
   plutil -p "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/Contents/Info.plist"
   ```

   Expected values:
   - `CFBundleExecutable` should be `PythonRunnerHorosPlugin`
   - `pluginType` should be `imageFilter`

**Solutions:**

**Solution A: Code signing issue**
```bash
# Re-sign the plugin with ad-hoc signature
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# Verify signature
codesign -dv "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Solution B: Quarantine attributes**
macOS may quarantine downloaded plugins:
```bash
# Remove quarantine attribute
xattr -dr com.apple.quarantine \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# Verify attributes removed
xattr -l "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Solution C: Restart required**
Always restart Horos/OsiriX after installing plugins:
1. Quit the application completely (⌘Q)
2. Wait 5 seconds
3. Relaunch the application

### Plugin appears but menu item is grayed out

**Symptoms:**
- Plugin shows as "Loaded" in Plugin Manager
- Menu item exists but is disabled/grayed out

**Cause:**
Image Filter plugins only work when a 2D viewer window is active.

**Solution:**

1. Open any study in Horos/OsiriX
2. Double-click a series to open the 2D viewer
3. **Ensure the 2D viewer window is in front (active)**
4. The menu item should now be enabled
5. Go to: `Plugins > Image Filters > PythonRunnerHorosPlugin > Run Python Script`

### Plugin crashes on launch

**Symptoms:**
- Horos/OsiriX crashes when plugin tries to load
- Console shows "dyld: Library not loaded"

**Diagnostic:**

Check Console.app for crash logs:
```bash
# View recent crash logs
log show --predicate 'eventMessage contains "Horos"' --last 10m
```

**Common causes:**

1. **Missing framework:** Plugin was built for wrong macOS SDK
   - **Solution:** Rebuild with correct Xcode/SDK version

2. **Architecture mismatch:** Intel plugin on Apple Silicon (or vice versa)
   - **Solution:** Rebuild for correct architecture
   ```bash
   ./build.sh horos  # Automatically detects architecture
   ```

3. **Corrupted plugin bundle:**
   - **Solution:** Clean rebuild
   ```bash
   ./build.sh horos  # Rebuilds from scratch
   ```

---

## Python Errors

### "Python not found" error

**Symptoms:**
- Alert shows: "Python execution failed"
- Console shows: `python3: command not found`

**Diagnostic:**

Check if Python 3 is installed:
```bash
python3 --version
which python3
```

**Solutions:**

**Solution A: Install Python 3**
```bash
# Using Homebrew (recommended)
brew install python3

# Verify installation
python3 --version
```

**Solution B: Python installed but not in PATH**
```bash
# Add to ~/.zshrc or ~/.bash_profile
echo 'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
which python3
```

**Solution C: Using Python.org installer**
- Download from: https://www.python.org/downloads/
- Install the `.pkg` file
- Restart Terminal
- Verify with `python3 --version`

### Python script execution fails

**Symptoms:**
- Alert shows: "Python script exited with status 1"
- Console shows error messages from Python

**Diagnostic steps:**

1. **Test the script directly:**
   ```bash
   # Navigate to plugin bundle
   cd "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/Contents/Resources/python_script"

   # Run script directly
   python3 main.py
   ```

2. **Check script permissions:**
   ```bash
   ls -la main.py
   ```

   Should show: `-rw-r--r--` or `-rwxr-xr-x`

**Common causes and solutions:**

**Cause A: Syntax errors in script**
- **Solution:** Fix Python syntax errors shown in Console output

**Cause B: Missing Python dependencies**
- **Solution:** Install required packages or set up virtual environment (see Virtual Environment section)

**Cause C: Script file not found**
- **Diagnostic:** Check if `main.py` exists in bundle
  ```bash
  ls -la "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/Contents/Resources/python_script/main.py"
  ```
- **Solution:** Copy your script to the correct location

### Module import errors

**Symptoms:**
- Python script runs but shows: `ModuleNotFoundError: No module named 'xxx'`
- Script requires packages not in standard library

**Solutions:**

**Option 1: Install packages system-wide (simple but not isolated)**
```bash
pip3 install package-name
```

**Option 2: Use virtual environment (recommended)**

See [Virtual Environment Problems](#virtual-environment-problems) section below for complete setup.

**Option 3: Bundle packages with plugin**

1. Create `requirements.txt`:
   ```txt
   numpy==1.24.0
   pillow==9.5.0
   ```

2. Install to plugin bundle:
   ```bash
   pip3 install -r requirements.txt \
     --target "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/Contents/Resources/python_packages"
   ```

3. Update `main.py` to add packages to path:
   ```python
   import sys
   import os

   # Add bundled packages to path
   bundle_path = os.path.dirname(os.path.dirname(__file__))
   packages_path = os.path.join(bundle_path, 'python_packages')
   sys.path.insert(0, packages_path)

   # Now imports work
   import numpy as np
   ```

---

## Codesigning Issues

### "Code signature invalid" error

**Symptoms:**
- Plugin not loading
- Console.app shows: `code signature invalid`
- macOS refuses to load the plugin

**Solution:**

Apply ad-hoc code signature:
```bash
# For Horos
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# For OsiriX
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/OsiriX/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Verify it worked:**
```bash
codesign -dv --verbose=4 \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

Expected output should include:
```
Signature=adhoc
```

### Gatekeeper blocking plugin

**Symptoms:**
- macOS shows: "PythonRunnerHorosPlugin.osirixplugin cannot be opened because the developer cannot be verified"
- Plugin quarantined after download

**Solution:**

**Method 1: Remove quarantine attribute (recommended)**
```bash
xattr -dr com.apple.quarantine \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Method 2: Allow in System Settings**
1. Go to: System Settings > Privacy & Security
2. Scroll down to "Security" section
3. Look for message about blocked plugin
4. Click "Allow Anyway"
5. Restart Horos/OsiriX

**Method 3: Disable Gatekeeper temporarily (not recommended)**
```bash
sudo spctl --master-disable  # Disable Gatekeeper
# ... install plugin ...
sudo spctl --master-enable   # Re-enable Gatekeeper
```

### Signing after modifying plugin contents

**Scenario:**
You edited `main.py` or added files to the plugin bundle.

**Problem:**
Modifying signed bundles invalidates the signature.

**Solution:**

Always re-sign after modifications:
```bash
# After editing files in the bundle, re-sign
codesign --force --deep --sign - \
  "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

**Tip:** Create a shell alias for convenience:
```bash
# Add to ~/.zshrc
alias resign-horos='codesign --force --deep --sign - "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"'

# Usage
resign-horos
```

---

## Virtual Environment Problems

### Virtual environment not found or invalid

**Symptoms:**
- Preferences show selected venv path but plugin uses system Python
- Console shows: "Using system Python (venv not configured or invalid)"

**Diagnostic:**

1. **Check if venv path is valid:**
   ```bash
   # Replace with your venv path
   ls -la /path/to/your/venv/bin/python3
   ```

2. **Verify venv is functional:**
   ```bash
   /path/to/your/venv/bin/python3 --version
   ```

**Solutions:**

**Solution A: Venv path doesn't exist**
- Create a new venv at the expected location:
  ```bash
  python3 -m venv /path/to/your/venv
  ```
- Re-select it in Preferences

**Solution B: Venv is corrupted**
- Delete and recreate:
  ```bash
  rm -rf /path/to/your/venv
  python3 -m venv /path/to/your/venv
  ```

**Solution C: Wrong path selected**
- Open plugin Preferences
- Click "Select Virtual Environment..."
- Navigate to the correct venv directory
- Click "Select"

### Cannot create virtual environment from preferences

**Symptoms:**
- "Create New Virtual Environment" button does nothing
- Error shown: "Failed to create virtual environment"

**Diagnostic:**

Test venv creation manually:
```bash
# Try creating a venv manually
python3 -m venv ~/test_venv

# Check if it worked
ls -la ~/test_venv/bin/python3
```

**Solutions:**

**Solution A: venv module not available**
```bash
# On some Python installations, venv is separate
# For Homebrew Python:
brew install python3

# For system Python on older macOS:
# Upgrade to newer macOS or install Python from python.org
```

**Solution B: No write permission to target directory**
```bash
# Try creating venv in your home directory
mkdir -p ~/venvs
python3 -m venv ~/venvs/horos_plugin_env
```

Then select `~/venvs/horos_plugin_env` in preferences.

**Solution C: Disk space full**
```bash
# Check available disk space
df -h ~

# Clean up if needed
```

### Packages not installing in virtual environment

**Symptoms:**
- "Install Requirements" button shows error
- Console shows: `pip install` failures

**Diagnostic:**

1. **Verify requirements.txt exists:**
   ```bash
   ls -la python_script/requirements.txt
   ```

2. **Test pip manually:**
   ```bash
   /path/to/venv/bin/pip install -r python_script/requirements.txt
   ```

**Common causes and solutions:**

**Cause A: No internet connection**
- **Solution:** Connect to internet and retry

**Cause B: Package name typos in requirements.txt**
- **Solution:** Verify package names on PyPI
  ```bash
  cat python_script/requirements.txt
  # Fix any typos
  ```

**Cause C: Pip needs upgrade**
```bash
/path/to/venv/bin/pip install --upgrade pip
```

**Cause D: Package requires compilation but no compiler available**
```bash
# Install Xcode command line tools
xcode-select --install
```

**Cause E: Version conflicts**
- **Solution:** Relax version constraints in requirements.txt
  ```txt
  # Instead of:
  numpy==1.24.0

  # Use:
  numpy>=1.24.0
  ```

### Script runs but doesn't use virtual environment packages

**Symptoms:**
- Venv is configured and valid
- Auto-activate is enabled
- Script still fails with `ModuleNotFoundError`

**Diagnostic:**

Add debug output to your script:
```python
import sys
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")
```

Check Console.app output after running script.

**Expected output:**
```
Python executable: /path/to/your/venv/bin/python3
```

**Solutions:**

**Solution A: Auto-activate disabled**
- Open Preferences
- Ensure "Auto-activate virtual environment" is checked
- Restart Horos/OsiriX

**Solution B: Venv packages not installed**
```bash
# Install packages in the venv
/path/to/venv/bin/pip install -r requirements.txt

# Verify packages installed
/path/to/venv/bin/pip list
```

**Solution C: Plugin preferences not saved**
- Check UserDefaults:
  ```bash
  defaults read PythonRunnerPlugin.VenvPath
  defaults read PythonRunnerPlugin.AutoActivateVenv
  ```
- If empty, preferences aren't persisting - re-configure in UI

---

## Apple Silicon Issues

### Plugin not loading on M1/M2/M3 Mac

**Symptoms:**
- Plugin loads fine on Intel Mac but not on Apple Silicon
- Console shows architecture-related errors

**Diagnostic:**

1. **Check plugin architecture:**
   ```bash
   lipo -info "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin/Contents/MacOS/PythonRunnerHorosPlugin"
   ```

2. **Check Horos/OsiriX architecture:**
   ```bash
   # For Horos
   lipo -info /Applications/Horos.app/Contents/MacOS/Horos

   # For OsiriX
   lipo -info /Applications/OsiriX.app/Contents/MacOS/OsiriX
   ```

**Solutions:**

**Solution A: Architecture mismatch**

The plugin and host app must match architectures.

If Horos/OsiriX is running under Rosetta (x86_64):
```bash
# Build will automatically match host app architecture
./build.sh horos
```

If Horos/OsiriX is native arm64:
```bash
# Build script auto-detects and builds for arm64
./build.sh horos
```

**Solution B: Force specific architecture build**

Edit build script if needed, or build universal binary:
```bash
# In Xcode project, set ARCHS to "x86_64 arm64" for universal build
xcodebuild -project "Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj" \
  -configuration Release \
  ARCHS="x86_64 arm64" \
  clean build
```

### Python architecture mismatch

**Symptoms:**
- Plugin loads but Python script fails with: `Bad CPU type in executable`
- Different Python architecture than host app

**Diagnostic:**

Check Python architecture:
```bash
# System Python
file $(which python3)

# Venv Python (if using)
file /path/to/venv/bin/python3
```

**Solutions:**

**Solution A: Install correct architecture Python**

For Apple Silicon (arm64):
```bash
# Install native arm64 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install arm64 Python
brew install python3

# Verify
file $(which python3)
# Should show: Mach-O 64-bit executable arm64
```

For Rosetta (x86_64):
```bash
# Install x86_64 Homebrew
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install x86_64 Python
arch -x86_64 brew install python3
```

**Solution B: Use Universal Python**

Python from python.org includes both architectures:
- Download from: https://www.python.org/downloads/
- Install the universal installer
- Verify: `file /usr/local/bin/python3`

### Performance issues on Apple Silicon

**Symptoms:**
- Plugin works but runs slower than expected
- Console shows Rosetta warnings

**Diagnostic:**

Check if running under Rosetta:
```bash
sysctl sysctl.proc_translated
# Returns 1 if under Rosetta, 0 if native
```

**Solution:**

Ensure both Horos/OsiriX and Python are native arm64:

1. **Check Horos/OsiriX:**
   - Right-click app in Finder
   - Get Info
   - **Uncheck** "Open using Rosetta" if checked
   - Restart app

2. **Reinstall native Python:**
   ```bash
   # Uninstall x86 Python
   brew uninstall python3

   # Install native arm64 Python
   arch -arm64 brew install python3
   ```

3. **Rebuild plugin:**
   ```bash
   ./build.sh horos
   ```

---

## Build Failures

### "xcodebuild: error: Unable to find a destination"

**Symptoms:**
- Build fails immediately with destination error
- No compilation output

**Solution:**

Check Xcode installation:
```bash
# Verify Xcode is installed
xcode-select -p

# If not set, install command line tools
xcode-select --install

# Or set to Xcode.app
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### "xcodebuild: error: The project ... does not contain a scheme"

**Symptoms:**
- Build script can't find build configuration

**Solution:**

Verify project files exist:
```bash
ls -la Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj/

# Check for platform-specific project files
ls -la Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj/project_Horos.pbxproj
ls -la Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj/project_OsiriX.pbxproj
```

If files missing, re-clone repository:
```bash
cd ..
git clone https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin.git
```

### Build succeeds but no output plugin

**Symptoms:**
- `xcodebuild` shows "BUILD SUCCEEDED"
- No `.osirixplugin` file in `build/Release/`

**Diagnostic:**

Check build directory:
```bash
ls -la Python-Runner-Horos-Plugin/build/Release/
```

**Solutions:**

**Solution A: Build output in wrong location**
```bash
# Search for the plugin
find Python-Runner-Horos-Plugin -name "*.osirixplugin"
```

**Solution B: Clean and rebuild**
```bash
# Clean build artifacts
rm -rf Python-Runner-Horos-Plugin/build/

# Rebuild
./build.sh horos
```

**Solution C: Xcode configuration issue**

Open project in Xcode and check:
1. Target output is set to plugin bundle
2. Build settings include proper wrapper extension

### Signing errors during build

**Symptoms:**
- Build fails with: `Code signing "PythonRunnerHorosPlugin" failed`
- Xcode requests signing certificate

**Solution:**

The build script uses ad-hoc signing. If Xcode is requesting certificates:

1. **Open project in Xcode:**
   ```bash
   open Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj
   ```

2. **Update code signing settings:**
   - Select project in navigator
   - Select target "PythonRunnerHorosPlugin"
   - Go to "Signing & Capabilities"
   - Uncheck "Automatically manage signing"
   - Set "Signing Certificate" to "Sign to Run Locally"
   - Set "Code Signing Identity" to "-" (dash)

3. **Save and rebuild:**
   ```bash
   ./build.sh horos
   ```

### Build errors about missing frameworks

**Symptoms:**
- Compiler errors: `Framework 'XXX' not found`
- Missing Horos or OsiriX headers

**Cause:**
Building for wrong platform or framework paths incorrect.

**Solution:**

1. **Verify you're building for correct platform:**
   ```bash
   # For Horos
   ./build.sh horos

   # For OsiriX (requires OsiriX SDK)
   ./build.sh osirix
   ```

2. **For OsiriX builds:**
   - Ensure OsiriX or OsiriX SDK is installed
   - Framework search paths must point to OsiriX frameworks

3. **Check bridging header:**
   ```bash
   # Verify correct bridging header copied
   cat Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin-Bridging-Header.h
   ```

---

## Getting Help

If you're still experiencing issues after trying solutions in this guide:

### 1. Check Console Logs

macOS logs detailed diagnostic information:

```bash
# View real-time logs for Horos
log stream --predicate 'process == "Horos"' --level debug

# View recent Horos logs
log show --predicate 'process == "Horos"' --last 10m

# Search for plugin-specific messages
log show --predicate 'eventMessage contains "PythonRunner"' --last 1h
```

### 2. Collect Diagnostic Information

When reporting issues, include:

```bash
# System information
sw_vers
uname -m

# Python information
python3 --version
which python3

# Xcode information
xcodebuild -version
xcode-select -p

# Plugin status
ls -la "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
codesign -dv "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"

# Check for quarantine
xattr -l "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

### 3. Report Issues

- **GitHub Issues:** [Create an issue](https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin/issues)
- **Include:**
  - Complete error messages from Console.app
  - Diagnostic information from above
  - Steps to reproduce the problem
  - What you've already tried

### 4. Community Resources

- **Documentation:** See [README.md](../README.md) for complete documentation
- **Examples:** Check [EXAMPLES.md](EXAMPLES.md) for common use cases
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

---

## Quick Reference: Common Fixes

### Plugin won't load
```bash
# Re-sign and remove quarantine
codesign --force --deep --sign - "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
xattr -dr com.apple.quarantine "$HOME/Library/Application Support/Horos/Plugins/PythonRunnerHorosPlugin.osirixplugin"
```

### Python not found
```bash
# Install Python 3
brew install python3
```

### Build failed
```bash
# Clean and rebuild
rm -rf Python-Runner-Horos-Plugin/build/
./build.sh horos
```

### Menu item grayed out
```
1. Open a study
2. Double-click series to open 2D viewer
3. Ensure 2D viewer window is active (in front)
```

### Virtual environment issues
```bash
# Recreate venv
rm -rf /path/to/venv
python3 -m venv /path/to/venv
```

---

**Still stuck?** Open an issue on GitHub with your diagnostic information and we'll help you resolve it.
