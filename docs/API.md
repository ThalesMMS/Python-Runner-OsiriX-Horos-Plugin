# API Reference

Complete API documentation for the Python Runner plugin, covering plugin classes, Horos/OsiriX framework integration, virtual environment management, and Python script development.

---

## Table of Contents

- [Plugin Swift API](#plugin-swift-api)
  - [PythonRunnerPlugin](#pythonrunnerplugin)
  - [VenvManager](#venvmanager)
  - [VenvSettings](#venvsettings)
  - [PreferencesWindowController](#preferenceswindowcontroller)
- [Horos/OsiriX Framework API](#horososirix-framework-api)
  - [PluginFilter Base Class](#pluginfilter-base-class)
  - [ViewerController](#viewercontroller)
  - [DCMPix](#dcmpix)
  - [BrowserController](#browsercontroller)
- [Python Script API](#python-script-api)
  - [Script Structure](#script-structure)
  - [Output Handling](#output-handling)
  - [Virtual Environment Access](#virtual-environment-access)
- [Menu Actions](#menu-actions)
- [Error Handling](#error-handling)

---

## Plugin Swift API

### PythonRunnerPlugin

Main plugin class that orchestrates Python script execution and integrates with Horos/OsiriX.

**Inheritance:** `PluginFilter`

**Location:** `Plugin.swift`

#### Core Methods

##### `filterImage(_ menuName: String!) -> Int`

**Purpose:** Entry point called when user selects a menu item.

**Parameters:**
- `menuName`: The name of the menu item selected ("Run Python Script" or "Preferences")

**Returns:** `Int` (0 for success)

**Example:**
```swift
override func filterImage(_ menuName: String!) -> Int {
    guard let menuName = menuName,
          let action = MenuAction(rawValue: menuName) else {
        presentAlert(title: "Python Runner", message: "Unsupported action selected.")
        return 0
    }

    switch action {
    case .runScript:
        startRunFlow()
    case .preferences:
        showPreferences()
    }

    return 0
}
```

##### `initPlugin()`

**Purpose:** Called at plugin startup for initialization tasks.

**Usage:**
```swift
override func initPlugin() {
    NSLog("PythonRunnerPlugin loaded and ready.")
}
```

##### `isCertifiedForMedicalImaging() -> Bool`

**Purpose:** Indicates whether the plugin is certified for medical imaging use.

**Returns:** `Bool` (true if certified)

**Usage:**
```swift
override func isCertifiedForMedicalImaging() -> Bool {
    return true
}
```

#### Private Methods

##### `runPythonScript()`

**Purpose:** Executes the bundled Python script with virtual environment support.

**Flow:**
1. Resolves script path from bundle
2. Checks virtual environment settings
3. Selects Python interpreter (venv or system)
4. Executes script with process capture
5. Presents results via alert

**Example:**
```swift
private func runPythonScript() {
    guard let scriptURL = resolveScriptURL() else {
        presentAlert(title: "Python Runner", message: "Unable to locate python_script/main.py")
        return
    }

    let settings = VenvSettings.shared
    let venvManager = VenvManager()

    var pythonExecutable: URL
    var usesVenv = false

    if settings.autoActivateVenv,
       let venvPath = settings.selectedVenvPath,
       venvManager.validateVenv(at: venvPath) {
        pythonExecutable = URL(fileURLWithPath: "\(venvPath)/bin/python3")
        usesVenv = true
    } else {
        pythonExecutable = URL(fileURLWithPath: "/usr/bin/env")
    }

    let arguments: [String] = usesVenv ? [scriptURL.path] : ["python3", scriptURL.path]
    let result = runSystemProcess(executableURL: pythonExecutable, arguments: arguments)

    // Handle result...
}
```

##### `runSystemProcess(executableURL: URL, arguments: [String]) -> ProcessExecutionResult`

**Purpose:** Executes a system process and captures its output.

**Parameters:**
- `executableURL`: Path to the executable
- `arguments`: Command-line arguments

**Returns:** `ProcessExecutionResult` containing:
- `terminationStatus`: Exit code
- `stdout`: Standard output data
- `stderr`: Standard error data
- `error`: Optional execution error

**Features:**
- Async stdout/stderr capture via pipes
- Real-time output logging to console
- Waits for process completion
- Comprehensive error handling

**Example:**
```swift
let result = runSystemProcess(
    executableURL: URL(fileURLWithPath: "/usr/bin/python3"),
    arguments: ["script.py", "--verbose"]
)

if result.terminationStatus == 0 {
    print("Success!")
} else {
    let errorOutput = String(data: result.stderr, encoding: .utf8)
    print("Error: \(errorOutput ?? "Unknown error")")
}
```

##### `presentAlert(title: String, message: String)`

**Purpose:** Displays a modal alert to the user.

**Parameters:**
- `title`: Alert window title
- `message`: Alert message content

**Thread Safety:** Automatically dispatches to main thread if called from background.

**Example:**
```swift
presentAlert(title: "Success", message: "Python script executed successfully")
```

##### `logToConsole(_ message: String)`

**Purpose:** Logs messages to the Xcode console with plugin prefix.

**Parameters:**
- `message`: Message to log

**Output Format:** `[PythonRunnerPlugin] message`

**Example:**
```swift
logToConsole("Starting script execution")
// Output: [PythonRunnerPlugin] Starting script execution
```

#### Menu Actions

Available menu actions defined in `MenuAction` enum:

```swift
private enum MenuAction: String {
    case runScript = "Run Python Script"
    case preferences = "Preferences"
}
```

---

### VenvManager

Manages Python virtual environments including creation, validation, and package installation.

**Location:** `VenvManager.swift`

#### Methods

##### `createVenv(at path: String) -> VenvResult`

**Purpose:** Creates a new Python virtual environment at the specified path.

**Parameters:**
- `path`: Directory path where the venv should be created

**Returns:** `VenvResult` (`.success(String)` or `.failure(VenvError)`)

**Error Conditions:**
- `.pythonNotFound` - Python 3 is not available on the system
- `.creationFailed(String)` - Venv creation failed with details

**Example:**
```swift
let manager = VenvManager()
let result = manager.createVenv(at: "/Users/username/my-venv")

switch result {
case .success(let message):
    print(message) // "Virtual environment created at /Users/username/my-venv"
case .failure(let error):
    print("Error: \(error)")
}
```

**Implementation:**
```bash
python3 -m venv <path>
```

##### `validateVenv(at path: String) -> Bool`

**Purpose:** Validates that a virtual environment exists and is functional.

**Parameters:**
- `path`: Directory path of the venv to validate

**Returns:** `Bool` (true if valid, false otherwise)

**Validation Checks:**
1. Directory exists and is a directory
2. `bin/python3` executable exists
3. Python executable is functional (`python3 --version` succeeds)

**Example:**
```swift
let manager = VenvManager()
if manager.validateVenv(at: "/Users/username/my-venv") {
    print("Venv is valid")
} else {
    print("Venv is invalid or doesn't exist")
}
```

##### `installPackages(venvPath: String, requirementsPath: String) -> VenvResult`

**Purpose:** Installs packages from a requirements.txt file into a virtual environment.

**Parameters:**
- `venvPath`: Directory path of the virtual environment
- `requirementsPath`: Path to the requirements.txt file

**Returns:** `VenvResult` (`.success(String)` or `.failure(VenvError)`)

**Error Conditions:**
- `.invalidPath(String)` - Invalid venv path or requirements file not found
- `.installationFailed(String)` - pip install failed with details

**Example:**
```swift
let manager = VenvManager()
let result = manager.installPackages(
    venvPath: "/Users/username/my-venv",
    requirementsPath: "/Users/username/requirements.txt"
)

switch result {
case .success(let message):
    print(message) // "Packages installed successfully from ..."
case .failure(.invalidPath(let details)):
    print("Invalid path: \(details)")
case .failure(.installationFailed(let details)):
    print("Installation failed: \(details)")
default:
    break
}
```

**Implementation:**
```bash
<venvPath>/bin/pip install -r <requirementsPath>
```

##### `listPackages(venvPath: String) -> [String]`

**Purpose:** Lists all packages installed in a virtual environment.

**Parameters:**
- `venvPath`: Directory path of the virtual environment

**Returns:** Array of package strings in "package==version" format, empty array on failure

**Example:**
```swift
let manager = VenvManager()
let packages = manager.listPackages(venvPath: "/Users/username/my-venv")

for package in packages {
    print(package) // e.g., "numpy==1.24.2"
}
```

**Implementation:**
```bash
<venvPath>/bin/pip list --format=freeze
```

#### Error Types

```swift
enum VenvError: Error {
    case creationFailed(String)      // Venv creation failed
    case installationFailed(String)  // Package installation failed
    case invalidPath(String)         // Invalid venv or file path
    case pythonNotFound              // Python 3 not available
}
```

#### Result Types

```swift
enum VenvResult {
    case success(String)  // Success with message
    case failure(VenvError)  // Failure with error
}
```

---

### VenvSettings

Manages persistent virtual environment settings using UserDefaults.

**Pattern:** Singleton

**Location:** `VenvSettings.swift`

#### Properties

##### `shared: VenvSettings` (static)

**Purpose:** Shared singleton instance for application-wide access.

**Example:**
```swift
let settings = VenvSettings.shared
```

##### `selectedVenvPath: String?`

**Purpose:** Path to the selected virtual environment, or nil if not configured.

**Read/Write:** Both

**Example:**
```swift
// Get current path
if let path = VenvSettings.shared.selectedVenvPath {
    print("Venv path: \(path)")
}

// Set new path
VenvSettings.shared.selectedVenvPath = "/Users/username/my-venv"

// Clear path
VenvSettings.shared.selectedVenvPath = nil
```

**Storage:** UserDefaults key: `PythonRunnerPlugin.VenvPath`

##### `autoActivateVenv: Bool`

**Purpose:** Whether to automatically activate the virtual environment for script execution.

**Read/Write:** Both

**Default:** `true`

**Example:**
```swift
// Get current setting
let autoActivate = VenvSettings.shared.autoActivateVenv

// Enable auto-activation
VenvSettings.shared.autoActivateVenv = true

// Disable auto-activation
VenvSettings.shared.autoActivateVenv = false
```

**Storage:** UserDefaults key: `PythonRunnerPlugin.AutoActivateVenv`

##### `isConfigured: Bool` (computed)

**Purpose:** Returns true if a virtual environment path is configured.

**Read-only:** Yes

**Example:**
```swift
if VenvSettings.shared.isConfigured {
    print("Venv is configured")
} else {
    print("No venv configured")
}
```

#### Methods

##### `clearSettings()`

**Purpose:** Clears all virtual environment settings from UserDefaults.

**Example:**
```swift
VenvSettings.shared.clearSettings()
// Both selectedVenvPath and autoActivateVenv are now reset
```

---

### PreferencesWindowController

Window controller for the Preferences UI, managing virtual environment configuration.

**Inheritance:** `NSWindowController`

**Location:** `PreferencesWindowController.swift`

#### UI Outlets

```swift
@IBOutlet weak var venvPathField: NSTextField!
@IBOutlet weak var chooseVenvButton: NSButton!
@IBOutlet weak var createVenvButton: NSButton!
@IBOutlet weak var installPackagesButton: NSButton!
@IBOutlet weak var packageListView: NSTextView!
@IBOutlet weak var statusLabel: NSTextField!
@IBOutlet weak var autoActivateCheckbox: NSButton!
```

#### Actions

##### `@IBAction chooseVenv(_ sender: Any)`

**Purpose:** Opens file picker to select an existing virtual environment.

**Flow:**
1. Presents `NSOpenPanel` for directory selection
2. Validates selected directory as venv
3. Updates settings if valid
4. Refreshes package list

##### `@IBAction createNewVenv(_ sender: Any)`

**Purpose:** Creates a new virtual environment at user-specified location.

**Flow:**
1. Presents `NSSavePanel` for location selection
2. Creates venv using `VenvManager`
3. Updates settings on success
4. Refreshes package list

##### `@IBAction installPackages(_ sender: Any)`

**Purpose:** Installs packages from a requirements.txt file.

**Flow:**
1. Verifies venv is selected
2. Presents `NSOpenPanel` for requirements.txt file
3. Installs packages using `VenvManager`
4. Refreshes package list

##### `@IBAction autoActivateChanged(_ sender: NSButton)`

**Purpose:** Updates auto-activate setting when checkbox changes.

**Parameters:**
- `sender`: The checkbox button

##### `@IBAction refreshPackageList(_ sender: Any)`

**Purpose:** Refreshes the displayed list of installed packages.

#### Private Methods

##### `loadCurrentSettings()`

**Purpose:** Loads settings from VenvSettings and updates UI.

##### `selectVenv(at path: String)`

**Purpose:** Validates and selects a virtual environment.

**Async:** Yes (validation runs on background queue)

##### `createVenv(at path: String)`

**Purpose:** Creates a new virtual environment.

**Async:** Yes (creation runs on background queue)

**UI State:** Disables controls during creation

##### `installPackagesFromFile(requirementsPath: String, venvPath: String)`

**Purpose:** Installs packages from requirements file.

**Async:** Yes (installation runs on background queue)

**UI State:** Disables controls during installation

##### `refreshPackageList()`

**Purpose:** Loads and displays installed packages.

**Async:** Yes (listing runs on background queue)

##### `updateStatus(_ message: String)`

**Purpose:** Updates the status label with a message.

**Thread Safe:** Yes (dispatches to main thread)

##### `setControlsEnabled(_ enabled: Bool)`

**Purpose:** Enables or disables UI controls during long operations.

##### `presentAlert(title: String, message: String)`

**Purpose:** Presents a modal alert sheet.

**Thread Safe:** Yes (dispatches to main thread)

---

## Horos/OsiriX Framework API

The plugin integrates with the Horos/OsiriX framework through the `PluginFilter` base class and has access to various framework APIs.

### PluginFilter Base Class

Base class for all Horos/OsiriX plugins.

**Header:** `<Horos/PluginFilter.h>` or `<OsiriX/PluginFilter.h>`

#### Properties

##### `viewerController: ViewerController`

**Purpose:** Reference to the current (frontmost and active) 2D viewer window.

**Usage:**
```swift
let viewer = viewerController
// Access current viewer's data
```

#### Core Methods

##### `filterImage(_ menuName: String!) -> Int`

**Purpose:** Entry point for Image Filter plugins. Override this method.

**Parameters:**
- `menuName`: Name of the menu item that was selected

**Returns:** `Int` (typically 0)

##### `initPlugin()`

**Purpose:** Called at application startup. Override for initialization tasks.

**Usage:**
```swift
override func initPlugin() {
    // Perform initialization
}
```

##### `willUnload()`

**Purpose:** Called before plugin is unloaded (e.g., for updates).

**Usage:**
```swift
override func willUnload() {
    // Cleanup resources
}
```

##### `isCertifiedForMedicalImaging() -> Bool`

**Purpose:** Indicates if plugin is certified for medical imaging.

**Returns:** `Bool` (true if certified)

#### Utility Methods

##### `viewerControllersList() -> [ViewerController]`

**Purpose:** Returns list of all open viewer windows.

**Returns:** Array of `ViewerController` objects

**Example:**
```swift
let viewers = viewerControllersList()
for viewer in viewers {
    // Process each viewer
}
```

##### `duplicateCurrent2DViewerWindow() -> ViewerController`

**Purpose:** Creates a new 2D viewer window with a copy of the current series.

**Returns:** New `ViewerController` instance

#### Plugin Types

The framework supports multiple plugin types:

- **Image Filter:** Most common type, operates on images (override `filterImage:`)
- **Pre-Process:** Processes files before import (override `processFiles:`)
- **Report:** Manages reports for studies (override `report:action:`)

---

### ViewerController

Window controller for 2D image viewers.

**Header:** `<Horos/ViewerController.h>`

**Purpose:** Represents a 2D viewer window containing an image series.

#### Key Properties

```objective-c
@property DCMView *imageView;              // Current image view
@property NSMutableArray *pixList;         // Array of DCMPix objects
@property NSMutableArray *fileList;        // Array of DicomImage objects
@property NSArray *roiList;                // ROIs for all images
@property DicomStudy *currentStudy;        // Current study
@property DicomSeries *currentSeries;      // Current series
```

#### Common Methods

```objective-c
// Image navigation
- (void)setImageIndex:(NSInteger)index;
- (NSInteger)imageIndex;

// ROI management
- (void)addROI:(ROI *)roi;
- (NSMutableArray *)selectedROIs;

// Window/Level
- (void)setWLWW:(float)wl :(float)ww;
- (float)curWL;
- (float)curWW;
```

---

### DCMPix

Represents an image for display, including pixel data and DICOM attributes.

**Header:** `<Horos/DCMPix.h>`

**Purpose:** Container for image pixel data and metadata.

#### Key Properties

```objective-c
@property float *fImage;               // Float buffer of image data
@property NSString *sourceFile;        // Source file path
@property long width;                  // Image width in pixels
@property long height;                 // Image height in pixels
@property double originX, originY, originZ;  // Image origin in 3D space
@property double orientation[9];       // Image orientation vectors
@property float pixelSpacingX;         // Pixel spacing in X
@property float pixelSpacingY;         // Pixel spacing in Y
@property float sliceThickness;        // Slice thickness
```

#### Common Methods

```objective-c
// Pixel data access
- (float *)fImage;
- (void)computeROI:(ROI *)roi;

// Image properties
- (float)minValueOfSeries;
- (float)maxValueOfSeries;
```

---

### BrowserController

Window controller for the database browser window.

**Header:** `<Horos/BrowserController.h>`

**Purpose:** Manages the main database browser interface.

#### Common Methods

```objective-c
// Database access
- (DicomDatabase *)database;
- (NSArray *)databaseSelection;

// Study/Series operations
- (void)selectStudy:(DicomStudy *)study;
- (void)openViewerForStudy:(DicomStudy *)study;
```

---

### Accessing Framework Classes from Swift

Due to the bridging header, framework classes are available in Swift:

**Bridging Header:** `PythonRunnerHorosPlugin-Bridging-Header_Horos.h`

```objective-c
#import <Horos/PluginFilter.h>
#import <Horos/BrowserController.h>
#import <Horos/DicomStudy.h>
#import <Horos/DicomSeries.h>
#import <Horos/DicomFile.h>
#import <Horos/DicomDatabase.h>
#import <Horos/ViewerController.h>
#import <Horos/DCMPix.h>
#import <Horos/ThreadsManager.h>
#import <DCM/DCMObject.h>
```

**Swift Usage:**
```swift
// Access viewer controller
let viewer = viewerController

// Get current image
if let imageView = viewer.imageView {
    let currentIndex = viewer.imageIndex()
    // Process image
}

// Access pixel data
if let pixList = viewer.pixList as? [DCMPix],
   let currentPix = pixList.first {
    let width = currentPix.width
    let height = currentPix.height
    // Process pixel data
}
```

---

## Python Script API

### Script Structure

Python scripts are bundled in the plugin and executed by the Plugin class.

**Location:** `Contents/Resources/python_script/main.py`

**Basic Template:**

```python
#!/usr/bin/env python3
#
# main.py
# PythonRunner
#
# Python script to be run by the Horos plugin
#

def main():
    """Main entry point for the script."""
    print("Hello from Python!", flush=True)

    # Your code here

if __name__ == "__main__":
    main()
```

### Output Handling

#### Standard Output

**Immediately Flushed Output:**

```python
# Use flush=True to see output immediately in Xcode console
print("Processing started...", flush=True)
```

**Why flush=True?**
- Output is captured via pipes
- Buffering can delay messages
- `flush=True` ensures immediate visibility in console

#### Standard Error

```python
import sys

# Write to stderr for error messages
print("Error: Something went wrong", file=sys.stderr, flush=True)
```

#### Exit Codes

```python
import sys

def main():
    try:
        # Your code here
        if success:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
```

**Exit Code Handling:**
- `0` = Success
- Non-zero = Failure (error message shown to user)

### Virtual Environment Access

When a virtual environment is configured and auto-activate is enabled, your script runs with the venv's Python interpreter and has access to installed packages.

**Script Example:**

```python
#!/usr/bin/env python3

def main():
    print("Checking environment...", flush=True)

    # Import packages from venv
    try:
        import numpy as np
        print(f"NumPy version: {np.__version__}", flush=True)
    except ImportError:
        print("NumPy not available", flush=True)

    # Check Python version
    import sys
    print(f"Python: {sys.version}", flush=True)
    print(f"Executable: {sys.executable}", flush=True)

if __name__ == "__main__":
    main()
```

**Output When Venv Active:**
```
[PythonRunnerPlugin] Using virtual environment Python: /Users/username/my-venv/bin/python3
Checking environment...
NumPy version: 1.24.2
Python: 3.11.2
Executable: /Users/username/my-venv/bin/python3
```

### Advanced Patterns

#### Error Handling

```python
import sys
import traceback

def main():
    try:
        # Your processing code
        result = process_data()
        print(f"Success: {result}", flush=True)

    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Command-Line Arguments

Scripts can accept arguments (would require modifying Plugin.swift to pass them):

```python
import sys

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"Processing: {input_file}", flush=True)
    else:
        print("No arguments provided", flush=True)

if __name__ == "__main__":
    main()
```

#### Progress Updates

```python
def main():
    total = 100
    for i in range(total):
        # Your processing
        if i % 10 == 0:
            progress = (i / total) * 100
            print(f"Progress: {progress:.0f}%", flush=True)

    print("Complete!", flush=True)
```

---

## Menu Actions

The plugin registers two menu items in the Horos/OsiriX Plugins menu.

### Configuration

Menu items are defined in `Info.plist`:

```xml
<key>MenuTitles</key>
<array>
    <string>Run Python Script</string>
    <string>-</string>
    <string>Preferences</string>
</array>
```

**Note:** `-` creates a separator line in the menu.

### Run Python Script

**Menu Item:** "Run Python Script"

**Action:** Executes the bundled Python script (`python_script/main.py`)

**Behavior:**
1. Runs on background queue to avoid blocking UI
2. Checks virtual environment settings
3. Selects Python interpreter (venv or system python3)
4. Executes script with output capture
5. Displays result alert when complete

**User Experience:**
- Click menu item
- Script executes (may take seconds to minutes)
- Alert shows when complete with status message

### Preferences

**Menu Item:** "Preferences"

**Action:** Opens the Preferences window for virtual environment configuration

**Window Features:**
- **Venv Path Field:** Shows currently selected venv path
- **Choose Venv Button:** Select existing venv directory
- **Create New Venv Button:** Create new venv at chosen location
- **Install Packages Button:** Install from requirements.txt
- **Package List View:** Shows installed packages
- **Auto-Activate Checkbox:** Enable/disable automatic venv activation
- **Status Label:** Shows operation status

**User Workflows:**

1. **Select Existing Venv:**
   - Click "Choose Venv"
   - Navigate to venv directory
   - Select and confirm
   - Validation occurs automatically

2. **Create New Venv:**
   - Click "Create New Venv"
   - Choose location and name
   - Click "Create"
   - Wait for creation to complete

3. **Install Packages:**
   - Ensure venv is selected
   - Click "Install Packages"
   - Select requirements.txt file
   - Wait for installation to complete
   - Package list refreshes automatically

---

## Error Handling

### VenvError Types

```swift
enum VenvError: Error {
    case creationFailed(String)
    case installationFailed(String)
    case invalidPath(String)
    case pythonNotFound
}
```

#### Error Messages

**VenvError.pythonNotFound**
```
Python 3 is not installed or not found in PATH.

Please install Python 3 to use virtual environments.
```

**VenvError.creationFailed(details)**
```
Failed to create virtual environment:

<details from process output>
```

**VenvError.installationFailed(details)**
```
Failed to install packages:

<details from pip output>
```

**VenvError.invalidPath(details)**
```
Invalid path:

<details about what's wrong>
```

### Process Execution Errors

**Script Not Found:**
```
Unable to locate python_script/main.py in the plugin bundle.
```

**Execution Failed:**
```
Python execution failed: <error description>
```

**Non-Zero Exit:**
```
<Combined stdout and stderr from script>
```

**Fallback Message:**
```
Python script exited with status <code>.
```

### Error Handling Patterns

#### Swift Error Handling

```swift
let result = venvManager.createVenv(at: path)

switch result {
case .success(let message):
    // Handle success
    print(message)

case .failure(let error):
    // Handle specific errors
    switch error {
    case .pythonNotFound:
        presentAlert(title: "Python Not Found", message: "Install Python 3")
    case .creationFailed(let details):
        presentAlert(title: "Creation Failed", message: details)
    default:
        presentAlert(title: "Error", message: "\(error)")
    }
}
```

#### Python Error Reporting

```python
import sys

def main():
    try:
        # Your code
        pass
    except Exception as e:
        # Error details go to stderr
        print(f"Error: {e}", file=sys.stderr, flush=True)
        # Exit with non-zero code
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Result:** Error message from stderr is shown in the plugin's result alert.

### Thread Safety

All UI operations (alerts, window updates) are dispatched to the main thread:

```swift
private func presentAlert(title: String, message: String) {
    if !Thread.isMainThread {
        DispatchQueue.main.async { [weak self] in
            self?.presentAlert(title: title, message: message)
        }
        return
    }

    // Present alert on main thread
    let alert = NSAlert()
    alert.messageText = title
    alert.informativeText = message
    alert.runModal()
}
```

### Background Queue Operations

Long-running operations execute on background queues:

```swift
DispatchQueue.global(qos: .userInitiated).async { [weak self] in
    // Perform long operation
    let result = self?.venvManager.createVenv(at: path)

    // Update UI on main thread
    DispatchQueue.main.async {
        self?.handleResult(result)
    }
}
```

---

## See Also

- [Architecture Guide](ARCHITECTURE.md) - Internal architecture and design patterns
- [Getting Started](GETTING_STARTED.md) - Installation and quick start guide
- [Horos Developer Documentation](https://horosproject.org) - Official Horos framework docs
- [OsiriX Plugin Development](http://www.osirix-viewer.com/PlugIns.html) - OsiriX plugin development guide

---

**Last Updated:** February 2026
**Plugin Version:** 1.0
**Author:** Thales Matheus Mendonca Santos
