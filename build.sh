#!/bin/bash

# Build script for PythonRunnerHorosPlugin
# Usage: ./build.sh [horos|osirix|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/Python-Runner-Horos-Plugin"
PROJECT_DIR="$SOURCE_DIR/PythonRunnerHorosPlugin.xcodeproj"
RELEASES_DIR="$SCRIPT_DIR/Releases"

usage() {
    echo "Usage: $0 [horos|osirix|both]"
    echo "  horos  - Build for Horos"
    echo "  osirix - Build for OsiriX"
    echo "  both   - Build for both platforms"
    exit 1
}

build_for_platform() {
    local PLATFORM="$1"
    local PLATFORM_UPPER=$(echo "$PLATFORM" | tr '[:lower:]' '[:upper:]' | sed 's/OSIRIX/OsiriX/' | sed 's/HOROS/Horos/')

    echo "========================================"
    echo "Building for $PLATFORM_UPPER..."
    echo "========================================"

    # Copy platform-specific files
    echo "Copying $PLATFORM_UPPER project files..."
    cp "$PROJECT_DIR/project_${PLATFORM_UPPER}.pbxproj" "$PROJECT_DIR/project.pbxproj"
    cp "$SOURCE_DIR/PythonRunnerHorosPlugin-Bridging-Header_${PLATFORM_UPPER}.h" "$SOURCE_DIR/PythonRunnerHorosPlugin-Bridging-Header.h"

    # Clean and build
    echo "Building..."
    xcodebuild -project "$PROJECT_DIR" -configuration Release clean build 2>&1 | grep -E "(BUILD|error:|warning:)" || true

    # Check if build succeeded
    if [ -d "$SOURCE_DIR/build/Release/PythonRunnerHorosPlugin.osirixplugin" ]; then
        echo "Build successful!"

        # Create releases directory if needed
        mkdir -p "$RELEASES_DIR/$PLATFORM_UPPER"

        # Copy to releases
        rm -rf "$RELEASES_DIR/$PLATFORM_UPPER/PythonRunnerHorosPlugin.osirixplugin"
        cp -R "$SOURCE_DIR/build/Release/PythonRunnerHorosPlugin.osirixplugin" "$RELEASES_DIR/$PLATFORM_UPPER/"

        # Create zip
        echo "Creating zip..."
        cd "$RELEASES_DIR/$PLATFORM_UPPER"
        rm -f PythonRunnerHorosPlugin.osirixplugin.zip
        zip -r -q PythonRunnerHorosPlugin.osirixplugin.zip PythonRunnerHorosPlugin.osirixplugin
        cd - > /dev/null

        echo "Plugin copied to: $RELEASES_DIR/$PLATFORM_UPPER/"
        echo "Zip created: $RELEASES_DIR/$PLATFORM_UPPER/PythonRunnerHorosPlugin.osirixplugin.zip"
    else
        echo "Build failed!"
        exit 1
    fi
}

# Restore Horos as default after builds
restore_horos_default() {
    echo "Restoring Horos as default configuration..."
    cp "$PROJECT_DIR/project_Horos.pbxproj" "$PROJECT_DIR/project.pbxproj"
    cp "$SOURCE_DIR/PythonRunnerHorosPlugin-Bridging-Header_Horos.h" "$SOURCE_DIR/PythonRunnerHorosPlugin-Bridging-Header.h"
}

# Main
case "${1:-}" in
    horos)
        build_for_platform "horos"
        restore_horos_default
        ;;
    osirix)
        build_for_platform "osirix"
        restore_horos_default
        ;;
    both)
        build_for_platform "horos"
        echo ""
        build_for_platform "osirix"
        echo ""
        restore_horos_default
        echo "========================================"
        echo "Both builds completed successfully!"
        echo "========================================"
        ;;
    *)
        usage
        ;;
esac
