#!/usr/bin/env python3
#
# batch_processing.py
# PythonRunner Example Script
#
# Demonstrates batch processing of multiple DICOM studies and images.
# This example shows how to iterate through directories, process multiple
# files, handle errors gracefully, and report progress during batch operations.
#
# Thales Matheus Mendonca Santos - January 2026
#

import sys
from pathlib import Path
from typing import Dict, List, Tuple


def process_single_image(dicom_path: Path) -> Tuple[bool, Dict]:
    """
    Process a single DICOM image and extract key information.

    Args:
        dicom_path: Path to the DICOM file

    Returns:
        Tuple of (success: bool, result: dict)
        - success: True if processing succeeded, False otherwise
        - result: Dictionary with extracted info or error message
    """
    try:
        import pydicom
    except ImportError:
        return False, {'error': 'pydicom not installed'}

    try:
        # Read the DICOM file
        ds = pydicom.dcmread(dicom_path, stop_before_pixels=True)

        # Extract key information
        info = {
            'filename': dicom_path.name,
            'patient_id': ds.get('PatientID', 'N/A'),
            'study_uid': ds.get('StudyInstanceUID', 'N/A'),
            'series_number': ds.get('SeriesNumber', 'N/A'),
            'instance_number': ds.get('InstanceNumber', 'N/A'),
            'modality': ds.get('Modality', 'N/A'),
            'study_description': ds.get('StudyDescription', 'N/A'),
        }
        return True, info

    except Exception as e:
        return False, {'error': str(e), 'filename': dicom_path.name}


def find_dicom_files(directory: Path) -> List[Path]:
    """
    Recursively find all DICOM files in a directory.

    Args:
        directory: Path to search for DICOM files

    Returns:
        List of Path objects for DICOM files found
    """
    dicom_files = []

    # Look for common DICOM file extensions
    extensions = ['.dcm', '.dicom', '.DCM', '.DICOM']

    for ext in extensions:
        dicom_files.extend(directory.rglob(f'*{ext}'))

    # Also check files without extensions (common in DICOM archives)
    for file in directory.rglob('*'):
        if file.is_file() and not file.suffix and file.name != '.DS_Store':
            dicom_files.append(file)

    return sorted(dicom_files)


def group_by_study(results: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group processed results by study UID.

    Args:
        results: List of processing results

    Returns:
        Dictionary mapping study UIDs to lists of images
    """
    studies = {}

    for result in results:
        if 'study_uid' in result:
            study_uid = result['study_uid']
            if study_uid not in studies:
                studies[study_uid] = []
            studies[study_uid].append(result)

    return studies


def display_progress(current: int, total: int, filename: str):
    """
    Display processing progress.

    Args:
        current: Current file number
        total: Total number of files
        filename: Name of current file being processed
    """
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"[{current}/{total}] ({percentage:.1f}%) Processing: {filename}", flush=True)


def display_summary(results: List[Tuple[bool, Dict]], total_files: int):
    """
    Display a summary of batch processing results.

    Args:
        results: List of processing results
        total_files: Total number of files attempted
    """
    successful = sum(1 for success, _ in results if success)
    failed = total_files - successful

    print("\n" + "="*70, flush=True)
    print("BATCH PROCESSING SUMMARY", flush=True)
    print("="*70, flush=True)
    print(f"Total files processed: {total_files}", flush=True)
    print(f"Successful:            {successful} ({(successful/total_files)*100:.1f}%)", flush=True)
    print(f"Failed:                {failed} ({(failed/total_files)*100:.1f}%)", flush=True)

    # Group by study
    successful_results = [result for success, result in results if success]
    studies = group_by_study(successful_results)

    print(f"\nUnique studies found:  {len(studies)}", flush=True)

    # Display study information
    if studies:
        print("\n" + "-"*70, flush=True)
        print("STUDIES PROCESSED:", flush=True)
        print("-"*70, flush=True)

        for study_uid, images in studies.items():
            study_desc = images[0].get('study_description', 'N/A')
            patient_id = images[0].get('patient_id', 'N/A')
            modality = images[0].get('modality', 'N/A')

            print(f"\nStudy: {study_desc}", flush=True)
            print(f"  Patient ID: {patient_id}", flush=True)
            print(f"  Modality:   {modality}", flush=True)
            print(f"  Images:     {len(images)}", flush=True)
            print(f"  Study UID:  {study_uid[:50]}...", flush=True)

    # Display errors if any
    errors = [(result['filename'], result.get('error', 'Unknown error'))
              for success, result in results if not success]

    if errors:
        print("\n" + "-"*70, flush=True)
        print("ERRORS ENCOUNTERED:", flush=True)
        print("-"*70, flush=True)
        for filename, error in errors[:10]:  # Show first 10 errors
            print(f"  {filename}: {error}", flush=True)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors", flush=True)

    print("\n" + "="*70, flush=True)


def main():
    """
    Main entry point for the batch processing script.

    This script demonstrates how to:
    - Find and iterate through multiple DICOM files in directories
    - Process each image with error handling
    - Report progress during batch operations
    - Group results by study
    - Generate a comprehensive summary report
    - Handle failures gracefully without stopping the batch

    Usage:
        python batch_processing.py /path/to/dicom/directory

    Example:
        python batch_processing.py ~/DICOM_Data/Patient_Studies

    The script will:
    1. Recursively search for all DICOM files in the directory
    2. Process each file, extracting metadata
    3. Display progress as it processes
    4. Group results by study
    5. Show a summary with statistics and any errors

    Example Output:
        DICOM Batch Processor - Example Script
        ========================================

        Found 150 DICOM files in: /path/to/dicom/directory
        Starting batch processing...

        [1/150] (0.7%) Processing: IM-0001-0001.dcm
        [2/150] (1.3%) Processing: IM-0001-0002.dcm
        [3/150] (2.0%) Processing: IM-0001-0003.dcm
        ...
        [150/150] (100.0%) Processing: IM-0050-0003.dcm

        ======================================================================
        BATCH PROCESSING SUMMARY
        ======================================================================
        Total files processed: 150
        Successful:            148 (98.7%)
        Failed:                2 (1.3%)

        Unique studies found:  3

        ----------------------------------------------------------------------
        STUDIES PROCESSED:
        ----------------------------------------------------------------------

        Study: Brain MRI with Contrast
          Patient ID: 123456
          Modality:   MR
          Images:     50
          Study UID:  1.2.840.113619.2.55.3.12345678...

        Study: Chest CT
          Patient ID: 789012
          Modality:   CT
          Images:     75
          Study UID:  1.2.840.113619.2.55.3.98765432...

        Study: Abdominal CT
          Patient ID: 345678
          Modality:   CT
          Images:     23
          Study UID:  1.2.840.113619.2.55.3.11223344...

        ----------------------------------------------------------------------
        ERRORS ENCOUNTERED:
        ----------------------------------------------------------------------
          corrupted_file.dcm: Invalid DICOM file
          incomplete_header.dcm: Missing required DICOM tags

        ======================================================================

        Batch processing complete!
    """
    # Keep output immediate so it shows up in the Xcode console
    print("DICOM Batch Processor - Example Script", flush=True)
    print("========================================", flush=True)

    # Check for pydicom
    try:
        import pydicom
    except ImportError:
        print("\nError: pydicom is not installed.", file=sys.stderr, flush=True)
        print("Install with: pip install pydicom", file=sys.stderr, flush=True)
        print("\nNote: This is a demonstration script showing batch processing.", flush=True)
        print("To use this in your plugin:", flush=True)
        print("  1. Install pydicom in your virtual environment", flush=True)
        print("  2. Modify Plugin.swift to pass directory paths as arguments", flush=True)
        print("  3. Adapt this batch processing logic for your needs", flush=True)
        sys.exit(1)

    # Check if a directory path was provided
    if len(sys.argv) < 2:
        print("\nUsage: python batch_processing.py <path_to_dicom_directory>", flush=True)
        print("\nThis script will:", flush=True)
        print("  - Recursively find all DICOM files in the directory", flush=True)
        print("  - Process each file with progress reporting", flush=True)
        print("  - Handle errors gracefully and continue processing", flush=True)
        print("  - Group results by study", flush=True)
        print("  - Display a comprehensive summary", flush=True)
        sys.exit(0)

    # Get the directory path from command line arguments
    directory = Path(sys.argv[1])

    # Validate the directory exists
    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}", file=sys.stderr, flush=True)
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: Path is not a directory: {directory}", file=sys.stderr, flush=True)
        sys.exit(1)

    # Find all DICOM files
    print(f"\nSearching for DICOM files in: {directory}", flush=True)
    dicom_files = find_dicom_files(directory)

    if not dicom_files:
        print("No DICOM files found in the specified directory.", flush=True)
        sys.exit(0)

    print(f"Found {len(dicom_files)} DICOM files", flush=True)
    print("Starting batch processing...\n", flush=True)

    # Process all files with progress reporting
    results = []
    for idx, dicom_file in enumerate(dicom_files, start=1):
        display_progress(idx, len(dicom_files), dicom_file.name)

        # Process the file
        success, result = process_single_image(dicom_file)
        results.append((success, result))

        # Add a small delay every 10 files to avoid overwhelming the console
        # (removed in production, but useful for demonstration)
        # if idx % 10 == 0:
        #     import time
        #     time.sleep(0.1)

    # Display summary
    display_summary(results, len(dicom_files))

    print("\nBatch processing complete!", flush=True)


if __name__ == "__main__":
    # Explicit entrypoint for direct execution
    main()
