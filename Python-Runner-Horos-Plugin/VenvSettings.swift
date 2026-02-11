//
// VenvSettings.swift
// PythonRunner
//
// Manages persistent storage of virtual environment settings using UserDefaults.
//
// Thales Matheus Mendonca Santos - February 2026
//

import Foundation

/// Manages virtual environment settings stored in UserDefaults
class VenvSettings {

    // MARK: - UserDefaults Keys

    private enum Keys {
        static let venvPath = "PythonRunnerPlugin.VenvPath"
        static let autoActivate = "PythonRunnerPlugin.AutoActivateVenv"
    }

    // MARK: - Properties

    /// The path to the selected virtual environment, or nil if not configured
    var selectedVenvPath: String? {
        get {
            return UserDefaults.standard.string(forKey: Keys.venvPath)
        }
        set {
            if let newValue = newValue {
                UserDefaults.standard.set(newValue, forKey: Keys.venvPath)
                logToConsole("Venv path saved: \(newValue)")
            } else {
                UserDefaults.standard.removeObject(forKey: Keys.venvPath)
                logToConsole("Venv path cleared")
            }
        }
    }

    /// Whether to automatically activate the virtual environment for script execution
    var autoActivateVenv: Bool {
        get {
            // Default to true if not explicitly set
            if UserDefaults.standard.object(forKey: Keys.autoActivate) == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: Keys.autoActivate)
        }
        set {
            UserDefaults.standard.set(newValue, forKey: Keys.autoActivate)
            logToConsole("Auto-activate venv set to: \(newValue)")
        }
    }

    // MARK: - Singleton

    /// Shared instance for application-wide access
    static let shared = VenvSettings()

    private init() {
        logToConsole("VenvSettings initialized")
    }

    // MARK: - Public Methods

    /// Clears all virtual environment settings from UserDefaults
    func clearSettings() {
        UserDefaults.standard.removeObject(forKey: Keys.venvPath)
        UserDefaults.standard.removeObject(forKey: Keys.autoActivate)
        logToConsole("All venv settings cleared")
    }

    /// Returns true if a virtual environment path is configured
    var isConfigured: Bool {
        return selectedVenvPath != nil
    }

    // MARK: - Private Helper Methods

    private func logToConsole(_ message: String) {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        NSLog("[VenvSettings] %@", trimmed)
    }
}
