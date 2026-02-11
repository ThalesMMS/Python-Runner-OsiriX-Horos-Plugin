//
// PreferencesWindowController.swift
// PythonRunner
//
// Window controller for managing virtual environment preferences.
// Allows creating, selecting, and configuring Python virtual environments.
//
// Thales Matheus Mendonca Santos - February 2026
//

import Cocoa

@objc
class PreferencesWindowController: NSWindowController {

    // MARK: - UI Outlets (to be connected in XIB)

    @IBOutlet weak var venvPathField: NSTextField!
    @IBOutlet weak var chooseVenvButton: NSButton!
    @IBOutlet weak var createVenvButton: NSButton!
    @IBOutlet weak var installPackagesButton: NSButton!
    @IBOutlet weak var packageListView: NSTextView!
    @IBOutlet weak var statusLabel: NSTextField!
    @IBOutlet weak var autoActivateCheckbox: NSButton!

    // MARK: - Properties

    private let venvManager = VenvManager()
    private let settings = VenvSettings.shared

    // MARK: - Initialization

    override init(window: NSWindow?) {
        super.init(window: window)
        commonInit()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        commonInit()
    }

    private func commonInit() {
        logToConsole("PreferencesWindowController initialized")
    }

    // MARK: - Window Lifecycle

    override func windowDidLoad() {
        super.windowDidLoad()
        logToConsole("Preferences window loaded")

        // Load current settings and refresh UI
        loadCurrentSettings()
        refreshPackageList()
    }

    // MARK: - Actions

    @IBAction func chooseVenv(_ sender: Any) {
        logToConsole("User clicked 'Choose Venv' button")

        let openPanel = NSOpenPanel()
        openPanel.canChooseFiles = false
        openPanel.canChooseDirectories = true
        openPanel.allowsMultipleSelection = false
        openPanel.message = "Select a Python virtual environment directory"
        openPanel.prompt = "Select"

        openPanel.beginSheetModal(for: window!) { [weak self] response in
            guard let self = self else { return }

            if response == .OK, let selectedURL = openPanel.url {
                let venvPath = selectedURL.path
                self.logToConsole("User selected venv path: \(venvPath)")
                self.selectVenv(at: venvPath)
            }
        }
    }

    @IBAction func createNewVenv(_ sender: Any) {
        logToConsole("User clicked 'Create New Venv' button")

        let savePanel = NSSavePanel()
        savePanel.canCreateDirectories = true
        savePanel.message = "Choose a location for the new virtual environment"
        savePanel.nameFieldStringValue = "venv"
        savePanel.prompt = "Create"

        savePanel.beginSheetModal(for: window!) { [weak self] response in
            guard let self = self else { return }

            if response == .OK, let selectedURL = savePanel.url {
                let venvPath = selectedURL.path
                self.logToConsole("User chose to create venv at: \(venvPath)")
                self.createVenv(at: venvPath)
            }
        }
    }

    @IBAction func installPackages(_ sender: Any) {
        logToConsole("User clicked 'Install Packages' button")

        guard let venvPath = settings.selectedVenvPath, !venvPath.isEmpty else {
            presentAlert(title: "No Virtual Environment", message: "Please select or create a virtual environment first.")
            return
        }

        let openPanel = NSOpenPanel()
        openPanel.canChooseFiles = true
        openPanel.canChooseDirectories = false
        openPanel.allowsMultipleSelection = false
        openPanel.allowedFileTypes = ["txt"]
        openPanel.message = "Select a requirements.txt file"
        openPanel.prompt = "Install"

        openPanel.beginSheetModal(for: window!) { [weak self] response in
            guard let self = self else { return }

            if response == .OK, let selectedURL = openPanel.url {
                let requirementsPath = selectedURL.path
                self.logToConsole("User selected requirements file: \(requirementsPath)")
                self.installPackagesFromFile(requirementsPath: requirementsPath, venvPath: venvPath)
            }
        }
    }

    @IBAction func autoActivateChanged(_ sender: NSButton) {
        let enabled = (sender.state == .on)
        settings.autoActivateVenv = enabled
        logToConsole("Auto-activate venv changed to: \(enabled)")
    }

    @IBAction func refreshPackageList(_ sender: Any) {
        logToConsole("User clicked refresh packages")
        refreshPackageList()
    }

    // MARK: - Private Helper Methods

    private func loadCurrentSettings() {
        // Load venv path
        if let venvPath = settings.selectedVenvPath {
            venvPathField?.stringValue = venvPath
            logToConsole("Loaded venv path: \(venvPath)")
        } else {
            venvPathField?.stringValue = "No virtual environment selected"
        }

        // Load auto-activate setting
        autoActivateCheckbox?.state = settings.autoActivateVenv ? .on : .off
    }

    private func selectVenv(at path: String) {
        updateStatus("Validating virtual environment...")

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let isValid = self.venvManager.validateVenv(at: path)

            DispatchQueue.main.async {
                if isValid {
                    self.settings.selectedVenvPath = path
                    self.venvPathField?.stringValue = path
                    self.updateStatus("Virtual environment selected successfully")
                    self.refreshPackageList()
                } else {
                    self.presentAlert(
                        title: "Invalid Virtual Environment",
                        message: "The selected directory is not a valid Python virtual environment."
                    )
                    self.updateStatus("Invalid virtual environment")
                }
            }
        }
    }

    private func createVenv(at path: String) {
        updateStatus("Creating virtual environment...")

        // Disable buttons during creation
        setControlsEnabled(false)

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let result = self.venvManager.createVenv(at: path)

            DispatchQueue.main.async {
                self.setControlsEnabled(true)

                switch result {
                case .success(let message):
                    self.settings.selectedVenvPath = path
                    self.venvPathField?.stringValue = path
                    self.updateStatus("Virtual environment created successfully")
                    self.presentAlert(title: "Success", message: message)
                    self.refreshPackageList()

                case .failure(let error):
                    let message = self.errorMessage(for: error)
                    self.updateStatus("Failed to create virtual environment")
                    self.presentAlert(title: "Creation Failed", message: message)
                }
            }
        }
    }

    private func installPackagesFromFile(requirementsPath: String, venvPath: String) {
        updateStatus("Installing packages...")

        // Disable buttons during installation
        setControlsEnabled(false)

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let result = self.venvManager.installPackages(
                venvPath: venvPath,
                requirementsPath: requirementsPath
            )

            DispatchQueue.main.async {
                self.setControlsEnabled(true)

                switch result {
                case .success(let message):
                    self.updateStatus("Packages installed successfully")
                    self.presentAlert(title: "Success", message: message)
                    self.refreshPackageList()

                case .failure(let error):
                    let message = self.errorMessage(for: error)
                    self.updateStatus("Failed to install packages")
                    self.presentAlert(title: "Installation Failed", message: message)
                }
            }
        }
    }

    private func refreshPackageList() {
        guard let venvPath = settings.selectedVenvPath, !venvPath.isEmpty else {
            packageListView?.string = "No virtual environment selected.\n\nSelect or create a virtual environment to view installed packages."
            return
        }

        updateStatus("Loading packages...")

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let packages = self.venvManager.listPackages(venvPath: venvPath)

            DispatchQueue.main.async {
                if packages.isEmpty {
                    self.packageListView?.string = "No packages installed.\n\nUse 'Install Packages' to install packages from a requirements.txt file."
                    self.updateStatus("No packages found")
                } else {
                    let packageText = packages.joined(separator: "\n")
                    self.packageListView?.string = packageText
                    self.updateStatus("\(packages.count) packages installed")
                    self.logToConsole("Displayed \(packages.count) packages")
                }
            }
        }
    }

    private func updateStatus(_ message: String) {
        DispatchQueue.main.async { [weak self] in
            self?.statusLabel?.stringValue = message
        }
    }

    private func setControlsEnabled(_ enabled: Bool) {
        chooseVenvButton?.isEnabled = enabled
        createVenvButton?.isEnabled = enabled
        installPackagesButton?.isEnabled = enabled
    }

    private func errorMessage(for error: VenvError) -> String {
        switch error {
        case .creationFailed(let details):
            return "Failed to create virtual environment:\n\n\(details)"
        case .installationFailed(let details):
            return "Failed to install packages:\n\n\(details)"
        case .invalidPath(let details):
            return "Invalid path:\n\n\(details)"
        case .pythonNotFound:
            return "Python 3 is not installed or not found in PATH.\n\nPlease install Python 3 to use virtual environments."
        }
    }

    private func presentAlert(title: String, message: String) {
        // Alerts must be presented on the main thread
        if !Thread.isMainThread {
            DispatchQueue.main.async { [weak self] in
                self?.presentAlert(title: title, message: message)
            }
            return
        }

        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = message
        alert.alertStyle = .informational

        if let window = self.window {
            alert.beginSheetModal(for: window, completionHandler: nil)
        } else {
            alert.runModal()
        }
    }

    private func logToConsole(_ message: String) {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        NSLog("[PreferencesWindowController] %@", trimmed)
    }
}
