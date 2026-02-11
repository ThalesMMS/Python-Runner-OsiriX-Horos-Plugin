# Contributing to Python Runner OsiriX/Horos Plugin

Thank you for your interest in contributing! This guide will help you set up your development environment and understand the contribution workflow.

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Building from Source](#building-from-source)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Your Changes](#testing-your-changes)
- [Pull Request Process](#pull-request-process)
- [Project Architecture](#project-architecture)
- [Common Development Tasks](#common-development-tasks)

---

## Development Environment Setup

### Prerequisites

Before you begin, ensure you have:

- **macOS**: 11.0 or later
- **Xcode**: 15 or 16+ (install from App Store)
- **Command Line Tools**: `xcode-select --install`
- **Python 3**: Available via `python3` in your PATH
- **Git**: For version control
- **Horos or OsiriX**: At least one platform installed for testing

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Python-Runner-OsiriX-Horos-Plugin.git
   cd Python-Runner-OsiriX-Horos-Plugin
   ```

2. **Verify your development environment**:
   ```bash
   # Check Xcode installation
   xcodebuild -version

   # Check Python availability
   python3 --version

   # Verify build script is executable
   chmod +x build.sh
   ```

3. **Install Horos or OsiriX** (if not already installed):
   - **Horos**: Download from [horosproject.org](https://horosproject.org/)
   - **OsiriX**: Available from the Mac App Store (paid)

4. **Set up your IDE**:
   - Open `Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj` in Xcode
   - Ensure the project builds successfully (⌘B)

---

## Building from Source

### Using the Build Script (Recommended)

The automated `build.sh` script handles all platform-specific configuration:

```bash
# Build for Horos (most common for open-source contributors)
./build.sh horos

# Build for OsiriX
./build.sh osirix

# Build for both platforms (useful before submitting PRs)
./build.sh both
```

**What the build script does**:
- Switches Xcode project configuration files (`project_Horos.pbxproj` or `project_OsiriX.pbxproj`)
- Copies the appropriate bridging header
- Runs `xcodebuild` with Release configuration
- Creates a zip file in `Releases/[Platform]/`
- Restores Horos as the default configuration (keeping the repo clean)

### Manual Building in Xcode

For development and debugging:

1. **Open the project**:
   ```bash
   open Python-Runner-Horos-Plugin/PythonRunnerHorosPlugin.xcodeproj
   ```

2. **Select the correct scheme** - Ensure the target matches your test platform

3. **Build** (⌘B) or **Build and Run** (⌘R)

**Note**: When building manually, you need to ensure the correct platform configuration is active. The `build.sh` script handles this automatically.

### Installing Your Build for Testing

After building, install to your plugins directory:

```bash
# For Horos
PLUGIN_DST="$HOME/Library/Application Support/Horos/Plugins/"
unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"
codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"

# For OsiriX
PLUGIN_DST="$HOME/Library/Application Support/OsiriX/Plugins/"
unzip -o Releases/OsiriX/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"
codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
```

Then restart Horos/OsiriX to load your changes.

---

## Code Style Guidelines

### Swift Code Style

Follow these conventions based on the existing codebase:

**File Headers**:
```swift
//
// YourFile.swift
// PythonRunner
//
// Brief description of the file's purpose.
//
// Your Name - Month Year
//
```

**Naming Conventions**:
- **Classes/Structs**: `PascalCase` (e.g., `VenvManager`, `ProcessExecutionResult`)
- **Functions/Variables**: `camelCase` (e.g., `filterImage`, `terminationStatus`)
- **Constants**: `camelCase` for local, `kConstantName` for static/global if needed
- **Enums**: `PascalCase` for the enum, `camelCase` for cases

**Code Organization**:
```swift
// 1. Imports
import Cocoa

// 2. Private helper types/structs
private struct ProcessExecutionResult {
    let terminationStatus: Int32
    let stdout: Data
    let stderr: Data
    let error: Error?
}

// 3. Main class
@objc(PythonRunnerPlugin)
class PythonRunnerPlugin: PluginFilter {
    // 4. Enums for menu actions or states
    private enum MenuAction: String {
        case runScript = "Run Python Script"
        case preferences = "Preferences"
    }

    // 5. Properties
    private var someProperty: String?

    // 6. Override methods
    override func filterImage(_ menuName: String!) -> Int {
        // Implementation
        return 0
    }

    // 7. Private helper methods
    private func helperMethod() {
        // Implementation
    }
}
```

**Error Handling**:
- Use guard statements for early exits
- Provide meaningful error messages
- Log to console using `NSLog` or `logToConsole` helper

**Example**:
```swift
guard let menuName = menuName,
      let action = MenuAction(rawValue: menuName) else {
    NSLog("PythonRunnerPlugin received unsupported menu action: %@", menuName ?? "nil")
    presentAlert(title: "Python Runner", message: "Unsupported action selected.")
    return 0
}
```

**Comments**:
- Use inline comments sparingly - prefer self-documenting code
- Document complex logic or non-obvious behavior
- Use `// MARK: -` for section organization in large files

### Python Code Style

For Python scripts in `python_script/`:

- Follow **PEP 8** style guidelines
- Use **4 spaces** for indentation
- Keep lines under **88 characters** (Black formatter standard)
- Use type hints where appropriate
- Include docstrings for functions and modules

**Example**:
```python
#!/usr/bin/env python3
"""
Module description.
"""

def process_images(image_paths: list[str]) -> dict:
    """
    Process a list of images.

    Args:
        image_paths: List of file paths to images

    Returns:
        Dictionary with processing results
    """
    results = {}
    # Implementation
    return results
```

### Shell Script Style

For `build.sh` and similar scripts:

- Use **4 spaces** for indentation
- Include `set -e` to exit on errors
- Add descriptive echo statements for user feedback
- Use meaningful variable names in `UPPER_CASE`
- Quote variable expansions: `"$VARIABLE"`

---

## Testing Your Changes

### Manual Testing Workflow

1. **Build the plugin**:
   ```bash
   ./build.sh horos  # or osirix
   ```

2. **Install to your test environment**:
   ```bash
   PLUGIN_DST="$HOME/Library/Application Support/Horos/Plugins/"
   unzip -o Releases/Horos/PythonRunnerHorosPlugin.osirixplugin.zip -d "$PLUGIN_DST"
   codesign --force --deep --sign - "$PLUGIN_DST/PythonRunnerHorosPlugin.osirixplugin"
   ```

3. **Restart Horos/OsiriX**

4. **Test the plugin**:
   - Open a study with a 2D viewer window
   - Go to `Plugins > Image Filters > PythonRunnerHorosPlugin`
   - Test each menu item you modified
   - Check Console.app for logs and errors

5. **Verify behavior**:
   - Check console output matches expectations
   - Verify Python script executes correctly
   - Test error handling (invalid inputs, missing files, etc.)
   - Confirm UI displays properly

### Testing Checklist

Before submitting a PR, verify:

- [ ] Plugin builds successfully with `./build.sh both`
- [ ] Plugin loads in Horos without errors (check Console.app)
- [ ] Plugin loads in OsiriX without errors (if you have access)
- [ ] All menu items function as expected
- [ ] Python scripts execute and produce correct output
- [ ] Error cases are handled gracefully
- [ ] Console logging is appropriate (not too verbose, not silent)
- [ ] No debug code or commented-out blocks remain
- [ ] Code follows style guidelines above

### Debugging Tips

**View Console Output**:
```bash
# Watch Horos logs in real-time
log stream --predicate 'subsystem contains "Horos"' --level debug

# Open Console.app and filter for "PythonRunner"
open -a Console
```

**Common Issues**:
- **Plugin doesn't appear**: Check Console.app for loading errors
- **Python script fails**: Verify Python 3 is in PATH, check script permissions
- **Codesign errors**: Re-run codesign command, ensure Xcode CLI tools installed
- **Build failures**: Clean build folder (`xcodebuild clean`), verify Xcode version

---

## Pull Request Process

### Before Submitting

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Test thoroughly** using the checklist above

4. **Build for both platforms**:
   ```bash
   ./build.sh both
   ```

5. **Update documentation** if needed:
   - Update `README.md` for user-facing changes
   - Update `docs/API.md` for API changes
   - Add examples to `docs/EXAMPLES.md` if relevant

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes

   - Detailed point 1
   - Detailed point 2
   - Fixes #issue_number (if applicable)"
   ```

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of what changed and why
   - Testing performed (platforms tested, scenarios covered)
   - Screenshots/console output if relevant
   - Any breaking changes or migration notes

### PR Review Process

- Maintainers will review your code for:
  - Code quality and style compliance
  - Functionality and correctness
  - Documentation completeness
  - Test coverage

- You may be asked to make changes - iterate on feedback
- Once approved, a maintainer will merge your PR

### After Your PR is Merged

- Delete your feature branch
- Pull the latest main branch
- Thank you for contributing!

---

## Project Architecture

Understanding the dual-platform architecture is crucial for contributing:

### Platform-Specific Files

The project maintains separate configurations for Horos and OsiriX:

```
PythonRunnerHorosPlugin.xcodeproj/
├── project.pbxproj                    # Active config (always Horos when not building)
├── project_Horos.pbxproj              # Horos-specific Xcode config
└── project_OsiriX.pbxproj             # OsiriX-specific Xcode config

Python-Runner-Horos-Plugin/
├── PythonRunnerHorosPlugin-Bridging-Header.h         # Active header
├── PythonRunnerHorosPlugin-Bridging-Header_Horos.h   # Horos header
└── PythonRunnerHorosPlugin-Bridging-Header_OsiriX.h  # OsiriX header
```

**The build.sh script**:
1. Copies the platform-specific `project_*.pbxproj` to `project.pbxproj`
2. Copies the platform-specific bridging header
3. Builds the plugin
4. Restores Horos as default (keeps the repo clean)

### Key Source Files

- **Plugin.swift**: Main plugin entry point, menu handling
- **VenvManager.swift**: Python virtual environment management
- **VenvSettings.swift**: Settings persistence
- **PreferencesWindowController.swift**: Preferences UI
- **Info.plist**: Plugin metadata (version, menu items, etc.)
- **python_script/**: Bundled Python scripts

### Frameworks

- **Horos.framework**: SDK for Horos (open-source)
- **OsiriXAPI.framework**: SDK for OsiriX (proprietary)

Both frameworks provide similar APIs, allowing dual-platform support with minimal code changes.

---

## Common Development Tasks

### Adding a New Menu Item

1. **Update Info.plist**:
   ```xml
   <key>MenuTitles</key>
   <array>
       <string>Run Python Script</string>
       <string>Preferences</string>
       <string>Your New Item</string>  <!-- Add here -->
   </array>
   ```

2. **Add enum case in Plugin.swift**:
   ```swift
   private enum MenuAction: String {
       case runScript = "Run Python Script"
       case preferences = "Preferences"
       case yourNewItem = "Your New Item"  // Add here
   }
   ```

3. **Handle in filterImage**:
   ```swift
   switch action {
   case .runScript:
       startRunFlow()
   case .preferences:
       showPreferences()
   case .yourNewItem:
       handleYourNewItem()  // Implement this method
   }
   ```

### Modifying Python Script Behavior

1. Edit `python_script/main.py` or add new scripts
2. Update Plugin.swift if changing execution parameters
3. Rebuild and test

### Updating Plugin Metadata

Edit `Info.plist`:
- `CFBundleVersion`: Build number (increment for each release)
- `CFBundleShortVersionString`: Version string (e.g., "1.0.0")
- `pluginType`: Keep as `imageFilter`
- `MenuTitles`: Plugin menu items

### Working with Frameworks

If you need to update the Horos or OsiriX frameworks:

1. Download the latest SDK from the respective source
2. Replace the `.framework` bundle
3. Update bridging headers if APIs changed
4. Test thoroughly on both platforms

---

## Questions or Need Help?

- **Check existing documentation**: `README.md`, `docs/` folder
- **Search issues**: Someone may have asked your question already
- **Open a discussion**: For general questions or ideas
- **File an issue**: For bugs or feature requests

Thank you for contributing to Python Runner OsiriX/Horos Plugin!
