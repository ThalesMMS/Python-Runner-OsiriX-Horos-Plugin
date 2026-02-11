#!/usr/bin/env python3
#
# basic_dicom_info.py
# PythonRunner Example Script
#
# Demonstrates DICOM data access and metadata extraction
# This example shows how to read DICOM files and extract patient information,
# study details, and image properties using pydicom.
#
# Thales Matheus Mendonca Santos - January 2026
#

import sys
from pathlib import Path


def extract_dicom_info(dicom_path):
    """
    Extract and display key DICOM metadata from a file.

    Args:
        dicom_path: Path to the DICOM file

    Returns:
        Dictionary containing extracted DICOM information
    """
    try:
        import pydicom
    except ImportError:
        print("Error: pydicom is not installed.", file=sys.stderr, flush=True)
        print("Install with: pip install pydicom", file=sys.stderr, flush=True)
        sys.exit(1)

    try:
        # Read the DICOM file
        print(f"Reading DICOM file: {dicom_path}", flush=True)
        ds = pydicom.dcmread(dicom_path)

        # Extract patient information
        patient_info = {
            'name': ds.get('PatientName', 'N/A'),
            'id': ds.get('PatientID', 'N/A'),
            'birth_date': ds.get('PatientBirthDate', 'N/A'),
            'sex': ds.get('PatientSex', 'N/A'),
        }

        # Extract study information
        study_info = {
            'description': ds.get('StudyDescription', 'N/A'),
            'date': ds.get('StudyDate', 'N/A'),
            'time': ds.get('StudyTime', 'N/A'),
            'uid': ds.get('StudyInstanceUID', 'N/A'),
        }

        # Extract series information
        series_info = {
            'description': ds.get('SeriesDescription', 'N/A'),
            'number': ds.get('SeriesNumber', 'N/A'),
            'modality': ds.get('Modality', 'N/A'),
            'uid': ds.get('SeriesInstanceUID', 'N/A'),
        }

        # Extract image properties
        image_info = {
            'rows': ds.get('Rows', 'N/A'),
            'columns': ds.get('Columns', 'N/A'),
            'instance_number': ds.get('InstanceNumber', 'N/A'),
            'slice_thickness': ds.get('SliceThickness', 'N/A'),
            'pixel_spacing': ds.get('PixelSpacing', 'N/A'),
        }

        return {
            'patient': patient_info,
            'study': study_info,
            'series': series_info,
            'image': image_info,
        }

    except FileNotFoundError:
        print(f"Error: File not found: {dicom_path}", file=sys.stderr, flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading DICOM file: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


def display_dicom_info(info):
    """
    Display extracted DICOM information in a readable format.

    Args:
        info: Dictionary containing DICOM information
    """
    print("\n" + "="*60, flush=True)
    print("DICOM FILE INFORMATION", flush=True)
    print("="*60, flush=True)

    # Display patient information
    print("\n[Patient Information]", flush=True)
    print(f"  Name:       {info['patient']['name']}", flush=True)
    print(f"  ID:         {info['patient']['id']}", flush=True)
    print(f"  Birth Date: {info['patient']['birth_date']}", flush=True)
    print(f"  Sex:        {info['patient']['sex']}", flush=True)

    # Display study information
    print("\n[Study Information]", flush=True)
    print(f"  Description: {info['study']['description']}", flush=True)
    print(f"  Date:        {info['study']['date']}", flush=True)
    print(f"  Time:        {info['study']['time']}", flush=True)
    print(f"  UID:         {info['study']['uid'][:40]}...", flush=True)

    # Display series information
    print("\n[Series Information]", flush=True)
    print(f"  Description: {info['series']['description']}", flush=True)
    print(f"  Number:      {info['series']['number']}", flush=True)
    print(f"  Modality:    {info['series']['modality']}", flush=True)
    print(f"  UID:         {info['series']['uid'][:40]}...", flush=True)

    # Display image properties
    print("\n[Image Properties]", flush=True)
    print(f"  Dimensions:      {info['image']['rows']} x {info['image']['columns']} pixels", flush=True)
    print(f"  Instance Number: {info['image']['instance_number']}", flush=True)
    print(f"  Slice Thickness: {info['image']['slice_thickness']} mm", flush=True)

    # Handle pixel spacing (can be a list of two values)
    pixel_spacing = info['image']['pixel_spacing']
    if isinstance(pixel_spacing, list) and len(pixel_spacing) == 2:
        print(f"  Pixel Spacing:   {pixel_spacing[0]} x {pixel_spacing[1]} mm", flush=True)
    else:
        print(f"  Pixel Spacing:   {pixel_spacing}", flush=True)

    print("\n" + "="*60, flush=True)


def main():
    """
    Main entry point for the DICOM info extraction script.

    This script demonstrates how to:
    - Read DICOM files using pydicom
    - Extract patient, study, series, and image metadata
    - Display information in a structured format
    - Handle errors gracefully

    Usage:
        python basic_dicom_info.py /path/to/dicom/file.dcm

    Example Output:
        Reading DICOM file: /path/to/sample.dcm

        ============================================================
        DICOM FILE INFORMATION
        ============================================================

        [Patient Information]
          Name:       Doe^John
          ID:         123456
          Birth Date: 19800101
          Sex:        M

        [Study Information]
          Description: Brain MRI with Contrast
          Date:        20240115
          Time:        143022
          UID:         1.2.840.113619.2.55.3.12345678...

        [Series Information]
          Description: T1 MPRAGE SAG
          Number:      3
          Modality:    MR
          UID:         1.2.840.113619.2.55.3.98765432...

        [Image Properties]
          Dimensions:      512 x 512 pixels
          Instance Number: 45
          Slice Thickness: 1.0 mm
          Pixel Spacing:   0.46875 x 0.46875 mm

        ============================================================
    """
    # Keep output immediate so it shows up in the Xcode console
    print("DICOM Info Extractor - Example Script", flush=True)
    print("======================================", flush=True)

    # Check if a DICOM file path was provided
    if len(sys.argv) < 2:
        print("\nUsage: python basic_dicom_info.py <path_to_dicom_file>", flush=True)
        print("\nNote: This is a demonstration script showing how to access DICOM data.", flush=True)
        print("To use this in your plugin:", flush=True)
        print("  1. Install pydicom in your virtual environment", flush=True)
        print("  2. Modify Plugin.swift to pass DICOM file paths as arguments", flush=True)
        print("  3. Replace main.py with this script or similar logic", flush=True)
        sys.exit(0)

    # Get the DICOM file path from command line arguments
    dicom_path = Path(sys.argv[1])

    # Validate the file exists
    if not dicom_path.exists():
        print(f"Error: File does not exist: {dicom_path}", file=sys.stderr, flush=True)
        sys.exit(1)

    # Extract and display DICOM information
    info = extract_dicom_info(dicom_path)
    display_dicom_info(info)

    print("\nProcessing complete!", flush=True)


if __name__ == "__main__":
    # Explicit entrypoint for direct execution
    main()
