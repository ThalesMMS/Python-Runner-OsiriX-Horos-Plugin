//
// Plugin.swift
// PythonRunner
//
// Minimal Horos plugin that runs a bundled Python script and shows an alert.
//
// Thales Matheus Mendonca Santos - January 2026
//

import Cocoa

// Captures process termination and output so the caller can decide how to report results.
private struct ProcessExecutionResult {
    let terminationStatus: Int32
    let stdout: Data
    let stderr: Data
    let error: Error?
}

@objc(PythonRunnerPlugin)
class PythonRunnerPlugin: PluginFilter {
    private enum MenuAction: String {
        case runScript = "Run Python Script"
    }

    override func filterImage(_ menuName: String!) -> Int {
        // Dispatch based on the selected menu item.
        logToConsole("filterImage invoked for menu action: \(menuName ?? "nil")")
        guard let menuName = menuName,
              let action = MenuAction(rawValue: menuName) else {
            NSLog("PythonRunnerPlugin received unsupported menu action: %@", menuName ?? "nil")
            presentAlert(title: "Python Runner", message: "Unsupported action selected.")
            return 0
        }

        switch action {
        case .runScript:
            startRunFlow()
        }

        return 0
    }

    override func initPlugin() {
        NSLog("PythonRunnerPlugin loaded and ready.")
    }

    override func isCertifiedForMedicalImaging() -> Bool {
        return true
    }

    private func startRunFlow() {
        // Run on a background queue to avoid blocking the UI.
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.runPythonScript()
        }
    }

    private func runPythonScript() {
        // Resolve the bundled script path before launching the process.
        guard let scriptURL = resolveScriptURL() else {
            presentAlert(title: "Python Runner", message: "Unable to locate python_script/main.py in the plugin bundle.")
            return
        }

        // Use /usr/bin/env so the user's PATH resolves python3.
        let result = runSystemProcess(
            executableURL: URL(fileURLWithPath: "/usr/bin/env"),
            arguments: ["python3", scriptURL.path]
        )

        let message: String
        if let error = result.error {
            message = "Python execution failed: \(error.localizedDescription)"
        } else if result.terminationStatus != 0 {
            // Surface stdout/stderr when the script exits with an error.
            let combined = result.stdout + result.stderr
            let details = String(data: combined, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
            let fallback = "Python script exited with status \(result.terminationStatus)."
            message = (details?.isEmpty == false ? details! : fallback)
        } else {
            message = "Python script ran. Search the Xcode console for a 'Hello world!!' message."
        }

        presentAlert(title: "Python Runner", message: message)
    }

    private func resolveScriptURL() -> URL? {
        // Prefer the python_script directory when present inside the bundle.
        let bundle = Bundle(for: type(of: self))
        if let url = bundle.url(forResource: "main", withExtension: "py", subdirectory: "python_script") {
            return url
        }
        return bundle.url(forResource: "main", withExtension: "py")
    }

    private func runSystemProcess(
        executableURL: URL,
        arguments: [String]
    ) -> ProcessExecutionResult {
        let process = Process()
        process.executableURL = executableURL
        process.arguments = arguments

        // Capture stdout/stderr so we can forward logs and error details.
        let stdoutPipe = Pipe()
        let stderrPipe = Pipe()
        process.standardOutput = stdoutPipe
        process.standardError = stderrPipe

        var capturedStdout = Data()
        var capturedStderr = Data()

        let stdoutHandle = stdoutPipe.fileHandleForReading
        let stderrHandle = stderrPipe.fileHandleForReading

        stdoutHandle.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            capturedStdout.append(data)

            if let message = String(data: data, encoding: .utf8), !message.isEmpty {
                self?.logToConsole(message)
            }
        }

        stderrHandle.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            capturedStderr.append(data)

            if let message = String(data: data, encoding: .utf8), !message.isEmpty {
                self?.logToConsole(message)
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
            return ProcessExecutionResult(terminationStatus: -1, stdout: capturedStdout, stderr: capturedStderr, error: error)
        }

        process.waitUntilExit()

        // Stop handlers and pull any remaining buffered output.
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

    private func presentAlert(title: String, message: String) {
        // Alerts must be presented on the main thread.
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

        if let browserWindow = BrowserController.currentBrowser()?.window {
            alert.beginSheetModal(for: browserWindow, completionHandler: nil)
        } else {
            alert.runModal()
        }
    }

    private func logToConsole(_ message: String) {
        // Avoid logging empty lines.
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        NSLog("[PythonRunner] %@", trimmed)
    }
}

extension PythonRunnerPlugin: NSMenuItemValidation {
    func validateMenuItem(_ menuItem: NSMenuItem) -> Bool {
        return true
    }
}
