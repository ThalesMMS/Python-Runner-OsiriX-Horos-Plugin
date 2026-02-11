# Plugin Architecture

This document explains the internal architecture of the Python Runner plugin, including its Swift components, Python integration mechanisms, virtual environment management, and dual-platform support.

---

## Table of Contents

- [Overview](#overview)
- [Plugin Structure](#plugin-structure)
- [Swift Components](#swift-components)
  - [Plugin.swift](#pluginswift)
  - [VenvManager.swift](#venvmanagerswift)
  - [VenvSettings.swift](#venvsettingsswift)
  - [PreferencesWindowController.swift](#preferenceswindowcontrollerswift)
- [Python Script Integration](#python-script-integration)
- [Virtual Environment Management](#virtual-environment-management)
- [Dual-Platform Support](#dual-platform-support)
- [Process Execution Architecture](#process-execution-architecture)
- [Threading Model](#threading-model)
- [Error Handling Strategy](#error-handling-strategy)

---

## Overview

The Python Runner plugin is a macOS bundle that integrates with Horos/OsiriX as an Image Filter plugin. It provides a bridge between the Swift-based medical imaging application and Python scripts, enabling users to execute custom Python code with access to virtual environments and package management.

### Key Design Principles

- **Minimal dependencies**: Pure Swift + system Python
- **Thread safety**: UI operations on main thread, I/O on background queues
- **Error resilience**: Graceful degradation with detailed error reporting
- **Platform agnostic**: Single codebase for Horos and OsiriX
- **User control**: Optional virtual environment configuration

---

## Plugin Structure

The plugin follows the standard macOS bundle structure required by Horos/OsiriX:

```
PythonRunnerHorosPlugin.osirixplugin/
├── Contents/
│   ├── Info.plist                  # Plugin metadata and configuration
│   ├── MacOS/
│   │   └── PythonRunnerHorosPlugin # Compiled binary
│   ├── Resources/
│   │   ├── python_script/
│   │   │   └── main.py             # Default Python script
│   │   └── PreferencesWindow.xib   # Preferences UI definition
│   └── Frameworks/
│       └── [Platform].framework    # Horos.framework or OsiriXAPI.framework
```

### Key Files

**Info.plist**
- Defines plugin metadata (name, version, bundle identifier)
- Specifies plugin type: `imageFilter`
- Declares menu items: "Run Python Script" and "Preferences"
- Sets minimum system requirements (macOS 11.0+)

**Plugin Binary**
- Compiled Swift code containing all plugin logic
- Dynamically linked to platform framework (Horos/OsiriX)
- Entry point: `PythonRunnerPlugin` class

**Python Script Directory**
- Bundled Python scripts that ship with the plugin
- Default script location: `Contents/Resources/python_script/main.py`
- Scripts can be modified post-installation

---

## Swift Components

The plugin consists of four main Swift components, each with a specific responsibility:

### Plugin.swift

**Purpose:** Main plugin entry point and orchestration layer.

**Key Responsibilities:**
- Implements `PluginFilter` protocol required by Horos/OsiriX
- Handles menu item selection and dispatches actions
- Manages Python script execution lifecycle
- Bridges Swift and Python process execution
- Presents UI alerts and error messages

**Architecture:**

```swift
@objc(PythonRunnerPlugin)
class PythonRunnerPlugin: PluginFilter {
    // Entry point - called when user selects menu item
    override func filterImage(_ menuName: String!) -> Int

    // Plugin lifecycle
    override func initPlugin()
    override func isCertifiedForMedicalImaging() -> Bool

    // Core functionality
    private func runPythonScript()
    private func resolveScriptURL() -> URL?
    private func runSystemProcess(...) -> ProcessExecutionResult
}
```

**Execution Flow:**

1. **Menu Selection** → `filterImage(_:)` called with menu item name
2. **Action Dispatch** → Routes to `runPythonScript()` or `showPreferences()`
3. **Background Execution** → Offloads work to `DispatchQueue.global()`
4. **Script Resolution** → Locates bundled Python script via `Bundle.url()`
5. **Environment Selection** → Checks `VenvSettings` for virtual environment
6. **Process Launch** → Executes Python via `Process` API
7. **Output Capture** → Streams stdout/stderr through pipes
8. **Result Presentation** → Shows alert dialog with execution status

**Process Execution:**

The plugin uses macOS `Process` API to execute Python:

```swift
let process = Process()
process.executableURL = pythonExecutable  // Either venv python or system python3
process.arguments = [scriptPath]
process.standardOutput = stdoutPipe       // Capture output
process.standardError = stderrPipe        // Capture errors
```

**Key Design Decision:**

The plugin supports two execution modes:
- **Virtual environment mode**: Uses Python from configured venv (`/path/to/venv/bin/python3`)
- **System mode**: Falls back to system Python via `/usr/bin/env python3`

The choice is made at runtime based on `VenvSettings.autoActivateVenv` and venv validation.

---

### VenvManager.swift

**Purpose:** Virtual environment lifecycle and package management.

**Key Responsibilities:**
- Create new Python virtual environments
- Validate existing virtual environments
- Install packages from requirements.txt
- List installed packages
- Execute venv-related system processes

**Architecture:**

```swift
class VenvManager {
    // Virtual environment operations
    func createVenv(at path: String) -> VenvResult
    func validateVenv(at path: String) -> Bool

    // Package management
    func installPackages(venvPath: String, requirementsPath: String) -> VenvResult
    func listPackages(venvPath: String) -> [String]

    // Internal utilities
    private func isPythonAvailable() -> Bool
    private func runSystemProcess(...) -> ProcessExecutionResult
}
```

**Virtual Environment Creation:**

1. Verifies Python 3 is available on the system
2. Executes: `python3 -m venv <path>`
3. Captures stdout/stderr for error reporting
4. Returns detailed success/failure result

**Virtual Environment Validation:**

Multi-step validation process:
1. Checks if directory exists and is a directory
2. Verifies presence of `bin/python3` executable
3. Tests executable by running `python3 --version`
4. Returns `true` only if all checks pass

**Package Installation:**

1. Validates target venv exists and is functional
2. Verifies requirements.txt file exists
3. Executes: `<venvPath>/bin/pip install -r <requirementsPath>`
4. Streams output to console for debugging
5. Returns detailed result with error messages

**Package Listing:**

1. Validates venv
2. Executes: `<venvPath>/bin/pip list --format=freeze`
3. Parses output into array of "package==version" strings
4. Returns empty array on failure (non-throwing)

**Error Handling:**

Uses custom `VenvError` enum for typed errors:
```swift
enum VenvError: Error {
    case creationFailed(String)
    case installationFailed(String)
    case invalidPath(String)
    case pythonNotFound
}
```

---

### VenvSettings.swift

**Purpose:** Persistent storage for virtual environment preferences.

**Key Responsibilities:**
- Store and retrieve venv path using UserDefaults
- Manage auto-activation preference
- Provide singleton access to settings
- Log configuration changes

**Architecture:**

```swift
class VenvSettings {
    // Singleton access
    static let shared = VenvSettings()

    // Persistent properties
    var selectedVenvPath: String? { get set }
    var autoActivateVenv: Bool { get set }

    // Utility
    var isConfigured: Bool { get }
    func clearSettings()
}
```

**UserDefaults Keys:**

- `PythonRunnerPlugin.VenvPath` - Path to selected virtual environment
- `PythonRunnerPlugin.AutoActivateVenv` - Boolean for auto-activation (default: `true`)

**Default Behavior:**

- If no venv is configured, returns `nil` for `selectedVenvPath`
- Auto-activation defaults to `true` on first launch
- Settings persist across plugin reloads and application restarts

**Usage Pattern:**

```swift
let settings = VenvSettings.shared
if settings.autoActivateVenv,
   let venvPath = settings.selectedVenvPath {
    // Use venv Python
} else {
    // Use system Python
}
```

---

### PreferencesWindowController.swift

**Purpose:** User interface for virtual environment management.

**Key Responsibilities:**
- Display current venv configuration
- Allow user to select existing venv
- Create new virtual environments
- Install packages from requirements.txt
- Display installed packages
- Toggle auto-activation setting

**Architecture:**

```swift
@objc
class PreferencesWindowController: NSWindowController {
    // UI Outlets (connected in XIB)
    @IBOutlet weak var venvPathField: NSTextField!
    @IBOutlet weak var packageListView: NSTextView!
    @IBOutlet weak var statusLabel: NSTextField!
    @IBOutlet weak var autoActivateCheckbox: NSButton!

    // Actions
    @IBAction func chooseVenv(_ sender: Any)
    @IBAction func createNewVenv(_ sender: Any)
    @IBAction func installPackages(_ sender: Any)
    @IBAction func autoActivateChanged(_ sender: NSButton)
}
```

**UI Workflow:**

**Choosing Existing Venv:**
1. User clicks "Choose Venv" button
2. `NSOpenPanel` presented for directory selection
3. Selected path validated via `VenvManager.validateVenv()`
4. If valid, path saved to `VenvSettings.shared`
5. Package list refreshed automatically

**Creating New Venv:**
1. User clicks "Create New Venv" button
2. `NSSavePanel` presented for location selection
3. Background task created for venv creation
4. Controls disabled during creation
5. On success, venv auto-selected and validated
6. Package list initialized (empty)

**Installing Packages:**
1. User clicks "Install Packages" button
2. `NSOpenPanel` presented for requirements.txt selection
3. Background task installs packages via pip
4. Installation output streamed to console
5. Package list refreshed on success
6. Errors displayed in alert dialog

**Threading:**

All long-running operations (validation, creation, installation) run on background queues:
```swift
DispatchQueue.global(qos: .userInitiated).async { [weak self] in
    // Perform work
    DispatchQueue.main.async {
        // Update UI
    }
}
```

This prevents UI freezing during potentially slow operations.

---

## Python Script Integration

### Script Resolution

The plugin locates Python scripts using the macOS `Bundle` API:

```swift
private func resolveScriptURL() -> URL? {
    let bundle = Bundle(for: type(of: self))

    // Prefer python_script subdirectory
    if let url = bundle.url(forResource: "main",
                           withExtension: "py",
                           subdirectory: "python_script") {
        return url
    }

    // Fallback to root Resources directory
    return bundle.url(forResource: "main", withExtension: "py")
}
```

### Execution Modes

**System Python Mode:**
```bash
/usr/bin/env python3 /path/to/plugin/python_script/main.py
```

**Virtual Environment Mode:**
```bash
/path/to/venv/bin/python3 /path/to/plugin/python_script/main.py
```

### Script Requirements

Python scripts must:
- Have a callable `main()` function or use `if __name__ == "__main__":`
- Use `flush=True` for print statements to ensure output appears in console
- Handle their own errors (uncaught exceptions appear in stderr)
- Exit with status code 0 for success, non-zero for failure

### Output Handling

**stdout:** Captured and logged to macOS Console with `[PythonRunner]` prefix

**stderr:** Captured and displayed in alert dialogs on script failure

**Example:**
```python
def main():
    print("This appears in Console.app", flush=True)
    # Errors here will be shown in alert dialog

if __name__ == "__main__":
    main()
```

---

## Virtual Environment Management

### Why Virtual Environments?

Virtual environments allow:
- Isolated package installations per project
- Different Python package versions for different scripts
- No system Python pollution
- Reproducible environments via requirements.txt

### Venv Lifecycle

**1. Creation:**
```bash
python3 -m venv /path/to/venv
```

Creates:
```
venv/
├── bin/
│   ├── python3       # Python interpreter
│   ├── pip           # Package installer
│   └── activate      # (Not used by plugin)
├── lib/
│   └── python3.x/
│       └── site-packages/  # Installed packages
└── pyvenv.cfg        # Venv configuration
```

**2. Validation:**

Checks performed:
- Directory exists and is a directory
- `bin/python3` exists
- `bin/python3 --version` exits with status 0

**3. Package Installation:**

```bash
/path/to/venv/bin/pip install -r requirements.txt
```

The plugin uses the venv's own pip, ensuring packages install to the correct location.

**4. Package Listing:**

```bash
/path/to/venv/bin/pip list --format=freeze
```

Output format:
```
numpy==1.24.0
pandas==2.0.0
pillow==10.0.0
```

### Auto-Activation

When `autoActivateVenv` is enabled:
1. Plugin checks if venv path is configured
2. Validates venv is functional
3. Uses venv's Python interpreter
4. Falls back to system Python if validation fails

When disabled:
- Always uses system Python (`/usr/bin/env python3`)
- Venv configuration ignored

---

## Dual-Platform Support

### Challenge

Horos and OsiriX have similar but incompatible plugin APIs:
- Different framework names (`Horos.framework` vs `OsiriXAPI.framework`)
- Different header imports
- Different plugin loading mechanisms

### Solution

The plugin uses **build-time configuration switching** via multiple Xcode project files:

```
PythonRunnerHorosPlugin.xcodeproj/
├── project.pbxproj                  # Active configuration (symlink)
├── project_Horos.pbxproj            # Horos build settings
└── project_OsiriX.pbxproj           # OsiriX build settings
```

**Bridging Headers:**

```
Python-Runner-Horos-Plugin/
├── PythonRunnerHorosPlugin-Bridging-Header_Horos.h    # Imports Horos SDK
└── PythonRunnerHorosPlugin-Bridging-Header_OsiriX.h   # Imports OsiriX SDK
```

### Build Process

The `build.sh` script automates platform switching:

1. **Save current configuration**
2. **Copy platform-specific project file** to `project.pbxproj`
3. **Build with xcodebuild**
4. **Copy plugin bundle** to `Releases/[Platform]/`
5. **Create distribution zip**
6. **Restore original configuration**

### Source Code Compatibility

**Key insight:** The plugin code uses only APIs common to both platforms:
- `PluginFilter` base class
- `BrowserController.currentBrowser()`
- `filterImage(_:)` callback
- Standard Swift/Cocoa APIs

No platform-specific code paths required in Swift files.

---

## Process Execution Architecture

### ProcessExecutionResult

Internal struct for capturing process execution details:

```swift
private struct ProcessExecutionResult {
    let terminationStatus: Int32  // Exit code (0 = success)
    let stdout: Data              // Captured stdout
    let stderr: Data              // Captured stderr
    let error: Error?             // Launch error (if any)
}
```

### Pipe Architecture

**Pipe Setup:**
```swift
let stdoutPipe = Pipe()
let stderrPipe = Pipe()
process.standardOutput = stdoutPipe
process.standardError = stderrPipe
```

**Real-time Streaming:**

Uses `readabilityHandler` for live output capture:

```swift
stdoutHandle.readabilityHandler = { [weak self] handle in
    let data = handle.availableData
    guard !data.isEmpty else { return }

    // Accumulate for final result
    capturedStdout.append(data)

    // Log immediately to console
    if let message = String(data: data, encoding: .utf8) {
        self?.logToConsole(message)
    }
}
```

**Cleanup:**

After process termination:
1. Stop readability handlers
2. Read remaining buffered data with `readDataToEndOfFile()`
3. Combine all captured output
4. Return comprehensive result

### Error Scenarios

**Launch Failure:**
- Executable not found
- Permission denied
- Returns `ProcessExecutionResult` with error and status -1

**Runtime Failure:**
- Python script has syntax error
- Script raises unhandled exception
- Returns non-zero termination status with stderr content

**Success:**
- Exit status 0
- stdout/stderr available for processing
- No error object

---

## Threading Model

### Main Thread Responsibilities

- All UI updates
- NSAlert presentation
- Menu item handling (initial entry point)
- Preferences window display

### Background Thread Responsibilities

- Python script execution
- Virtual environment operations (create, validate, install)
- File I/O operations
- System process execution

### Thread Coordination

**Pattern:**
```swift
DispatchQueue.global(qos: .userInitiated).async { [weak self] in
    // 1. Perform expensive work (I/O, process execution)
    let result = self?.performWork()

    DispatchQueue.main.async {
        // 2. Update UI with results
        self?.updateUI(with: result)
    }
}
```

**Quality of Service:**
- `.userInitiated` - User-triggered actions (script execution, venv creation)
- `.utility` - Background refresh operations (package list updates)

### Thread Safety

**Safe patterns:**
- `VenvSettings` uses `UserDefaults` (thread-safe)
- UI updates always dispatched to main queue
- Weak self captures prevent retain cycles

**Avoided patterns:**
- No mutable shared state between threads
- No synchronous waiting on background threads
- No blocking operations on main thread

---

## Error Handling Strategy

### Levels of Error Handling

**1. Fatal Errors → Alerts**
- Python script not found
- Permission errors
- Virtual environment creation failure

**2. Recoverable Errors → Fallback**
- Invalid venv configuration → Use system Python
- Venv validation failure → Disable venv mode
- Package list failure → Show empty list

**3. Informational → Console Logging**
- Script output
- Process execution details
- Configuration changes

### Error Presentation

**User-Facing Errors:**

```swift
presentAlert(
    title: "Python Runner",
    message: "Unable to locate python_script/main.py in the plugin bundle."
)
```

**Developer-Facing Errors:**

```swift
NSLog("[PythonRunner] Python execution failed: \(error.localizedDescription)")
```

### Error Message Construction

For script failures, the plugin combines all available information:

```swift
if result.terminationStatus != 0 {
    let combined = result.stdout + result.stderr
    let details = String(data: combined, encoding: .utf8)?
        .trimmingCharacters(in: .whitespacesAndNewlines)
    let fallback = "Python script exited with status \(result.terminationStatus)."
    message = (details?.isEmpty == false ? details! : fallback)
}
```

This ensures users see the actual Python error, not just a generic failure message.

---

## Summary

The Python Runner plugin architecture is designed for:

- **Simplicity**: Minimal components, clear responsibilities
- **Reliability**: Defensive programming, graceful degradation
- **Extensibility**: Easy to add new Python scripts or venv features
- **Maintainability**: Well-structured code, comprehensive logging
- **User Experience**: Background processing, informative error messages

The separation of concerns across four Swift components (`Plugin`, `VenvManager`, `VenvSettings`, `PreferencesWindowController`) creates a modular system where each component can be understood and modified independently.

The dual-platform support via build-time configuration ensures a single codebase serves both Horos and OsiriX users without runtime overhead or complex abstraction layers.

---

## Next Steps

For developers looking to extend the plugin:

1. **Add new Python scripts**: Place `.py` files in `python_script/` directory
2. **Customize execution**: Modify `runPythonScript()` to pass arguments or environment variables
3. **Enhance UI**: Extend `PreferencesWindowController` with additional configuration options
4. **Add menu items**: Update `Info.plist` `MenuTitles` array and add cases to `MenuAction` enum

See [GETTING_STARTED.md](./GETTING_STARTED.md) for build and installation instructions.
