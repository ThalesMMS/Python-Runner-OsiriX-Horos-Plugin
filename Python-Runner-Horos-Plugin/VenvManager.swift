//
// VenvManager.swift
// PythonRunner
//
// Manages Python virtual environments for the plugin.
// Handles creation, validation, package installation, and package listing.
//
// Thales Matheus Mendonca Santos - February 2026
//

import Foundation

enum VenvError: Error {
    case creationFailed(String)
    case installationFailed(String)
    case invalidPath(String)
    case pythonNotFound
}

// Result type for venv operations
enum VenvResult {
    case success(String)
    case failure(VenvError)
}

class VenvManager {

    // MARK: - Virtual Environment Creation

    /// Creates a new Python virtual environment at the specified path.
    /// - Parameter path: The directory path where the venv should be created
    /// - Returns: VenvResult indicating success or failure with details
    func createVenv(at path: String) -> VenvResult {
        logToConsole("Creating virtual environment at: \(path)")

        // Verify Python is available
        guard isPythonAvailable() else {
            return .failure(.pythonNotFound)
        }

        // Execute python3 -m venv <path>
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: "/usr/bin/env"),
            arguments: ["python3", "-m", "venv", path]
        )

        if let error = result.error {
            let message = "Failed to create venv: \(error.localizedDescription)"
            logToConsole(message)
            return .failure(.creationFailed(message))
        }

        if result.terminationStatus != 0 {
            let combined = result.stdout + result.stderr
            let details = String(data: combined, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let message = "Venv creation failed with status \(result.terminationStatus): \(details)"
            logToConsole(message)
            return .failure(.creationFailed(message))
        }

        logToConsole("Virtual environment created successfully at: \(path)")
        return .success("Virtual environment created at \(path)")
    }

    // MARK: - Virtual Environment Validation

    /// Validates that a virtual environment exists and is functional at the specified path.
    /// - Parameter path: The directory path of the venv to validate
    /// - Returns: true if the venv is valid, false otherwise
    func validateVenv(at path: String) -> Bool {
        logToConsole("Validating virtual environment at: \(path)")

        let fileManager = FileManager.default

        // Check if the venv directory exists
        var isDirectory: ObjCBool = false
        guard fileManager.fileExists(atPath: path, isDirectory: &isDirectory),
              isDirectory.boolValue else {
            logToConsole("Venv validation failed: directory does not exist")
            return false
        }

        // Check for the Python executable inside the venv
        let pythonPath = "\(path)/bin/python3"
        guard fileManager.fileExists(atPath: pythonPath) else {
            logToConsole("Venv validation failed: python3 executable not found")
            return false
        }

        // Verify the Python executable is functional
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: pythonPath),
            arguments: ["--version"]
        )

        if result.terminationStatus != 0 {
            logToConsole("Venv validation failed: python3 executable not functional")
            return false
        }

        logToConsole("Virtual environment validated successfully")
        return true
    }

    // MARK: - Package Management

    /// Installs packages into a virtual environment from a requirements.txt file.
    /// - Parameters:
    ///   - venvPath: The directory path of the virtual environment
    ///   - requirementsPath: The path to the requirements.txt file
    /// - Returns: VenvResult indicating success or failure with details
    func installPackages(venvPath: String, requirementsPath: String) -> VenvResult {
        logToConsole("Installing packages from \(requirementsPath) into venv at \(venvPath)")

        // Validate the venv exists
        guard validateVenv(at: venvPath) else {
            let message = "Invalid virtual environment at \(venvPath)"
            logToConsole(message)
            return .failure(.invalidPath(message))
        }

        // Verify requirements file exists
        let fileManager = FileManager.default
        guard fileManager.fileExists(atPath: requirementsPath) else {
            let message = "Requirements file not found at \(requirementsPath)"
            logToConsole(message)
            return .failure(.invalidPath(message))
        }

        // Execute <venvPath>/bin/pip install -r <requirementsPath>
        let pipPath = "\(venvPath)/bin/pip"
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: pipPath),
            arguments: ["install", "-r", requirementsPath]
        )

        if let error = result.error {
            let message = "Failed to install packages: \(error.localizedDescription)"
            logToConsole(message)
            return .failure(.installationFailed(message))
        }

        if result.terminationStatus != 0 {
            let combined = result.stdout + result.stderr
            let details = String(data: combined, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let message = "Package installation failed with status \(result.terminationStatus): \(details)"
            logToConsole(message)
            return .failure(.installationFailed(message))
        }

        logToConsole("Packages installed successfully")
        return .success("Packages installed successfully from \(requirementsPath)")
    }

    /// Lists all packages installed in a virtual environment.
    /// - Parameter venvPath: The directory path of the virtual environment
    /// - Returns: Array of package names with versions, or empty array on failure
    func listPackages(venvPath: String) -> [String] {
        logToConsole("Listing packages in venv at \(venvPath)")

        // Validate the venv exists
        guard validateVenv(at: venvPath) else {
            logToConsole("Cannot list packages: invalid venv")
            return []
        }

        // Execute <venvPath>/bin/pip list --format=freeze
        let pipPath = "\(venvPath)/bin/pip"
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: pipPath),
            arguments: ["list", "--format=freeze"]
        )

        if result.terminationStatus != 0 {
            logToConsole("Failed to list packages")
            return []
        }

        // Parse the output into package lines
        guard let output = String(data: result.stdout, encoding: .utf8) else {
            logToConsole("Failed to parse package list output")
            return []
        }

        let packages = output
            .components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }

        logToConsole("Found \(packages.count) packages")
        return packages
    }

    // MARK: - Private Helper Methods

    /// Checks if Python 3 is available on the system.
    /// - Returns: true if python3 is available, false otherwise
    private func isPythonAvailable() -> Bool {
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: "/usr/bin/env"),
            arguments: ["python3", "--version"]
        )
        return result.terminationStatus == 0
    }

    /// Executes a system process and captures its output.
    /// - Parameters:
    ///   - executableURL: The URL of the executable to run
    ///   - arguments: Array of command-line arguments
    /// - Returns: ProcessExecutionResult with status, stdout, stderr, and any error
    private func runSystemProcess(
        executableURL: URL,
        arguments: [String]
    ) -> ProcessExecutionResult {
        let process = Process()
        process.executableURL = executableURL
        process.arguments = arguments

        // Capture stdout/stderr for result processing
        let stdoutPipe = Pipe()
        let stderrPipe = Pipe()
        process.standardOutput = stdoutPipe
        process.standardError = stderrPipe

        var capturedStdout = Data()
        var capturedStderr = Data()

        let stdoutHandle = stdoutPipe.fileHandleForReading
        let stderrHandle = stderrPipe.fileHandleForReading

        stdoutHandle.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            capturedStdout.append(data)

            if let message = String(data: data, encoding: .utf8), !message.isEmpty {
                self.logToConsole(message)
            }
        }

        stderrHandle.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            capturedStderr.append(data)

            if let message = String(data: data, encoding: .utf8), !message.isEmpty {
                self.logToConsole(message)
            }
        }

        var launchError: Error?
        do {
            try process.run()
        } catch {
            launchError = error
        }

        if let error = launchError {
            stdoutHandle.readabilityHandler = nil
            stderrHandle.readabilityHandler = nil
            return ProcessExecutionResult(
                terminationStatus: -1,
                stdout: capturedStdout,
                stderr: capturedStderr,
                error: error
            )
        }

        process.waitUntilExit()

        // Stop handlers and pull any remaining buffered output
        stdoutHandle.readabilityHandler = nil
        stderrHandle.readabilityHandler = nil

        capturedStdout.append(stdoutHandle.readDataToEndOfFile())
        capturedStderr.append(stderrHandle.readDataToEndOfFile())

        return ProcessExecutionResult(
            terminationStatus: process.terminationStatus,
            stdout: capturedStdout,
            stderr: capturedStderr,
            error: nil
        )
    }

    private func logToConsole(_ message: String) {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        NSLog("[VenvManager] %@", trimmed)
    }
}

// MARK: - Supporting Types

// Captures process termination and output for venv operations
private struct ProcessExecutionResult {
    let terminationStatus: Int32
    let stdout: Data
    let stderr: Data
    let error: Error?
}
