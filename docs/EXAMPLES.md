# Example Scripts Guide

This guide provides detailed documentation for all example scripts included in the PythonRunner plugin. Each example demonstrates different capabilities and patterns for working with DICOM data in OsiriX/Horos.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Example 1: Basic DICOM Info](#example-1-basic-dicom-info)
- [Example 2: Batch Processing](#example-2-batch-processing)
- [Example 3: Custom Image Filters](#example-3-custom-image-filters)
- [General Tips](#general-tips)
- [Integrating Examples into Your Plugin](#integrating-examples-into-your-plugin)

---

## Overview

The example scripts demonstrate:

- **DICOM metadata extraction** - Reading and displaying patient, study, and image information
- **Batch processing** - Handling multiple files with progress reporting and error handling
- **Image processing** - Applying filters and manipulations to DICOM pixel data
- **Best practices** - Error handling, progress reporting, and clean output formatting

All examples are standalone scripts that can be run from the command line or integrated into your OsiriX/Horos plugin.

---

## Prerequisites

### Required Python Packages

Each example has different dependencies:

| Script | Required Packages |
|--------|------------------|
| `basic_dicom_info.py` | `pydicom` |
| `batch_processing.py` | `pydicom` |
| `custom_filter.py` | `pydicom`, `numpy`, `scipy` |

### Installation

Install required packages in your virtual environment:

```bash
# For basic_dicom_info and batch_processing
pip install pydicom

# For custom_filter (includes all dependencies)
pip install pydicom numpy scipy
```

### Test Data

To run the examples, you'll need DICOM files. You can:

- Use sample DICOM files from your OsiriX/Horos database
- Download test DICOM datasets from [Medical Imaging Datasets](https://www.cancerimagingarchive.net/)
- Generate test files using DICOM creation tools

---

## Example 1: Basic DICOM Info

**File:** `examples/basic_dicom_info.py`

### Overview

This example demonstrates how to extract and display comprehensive DICOM metadata from a single file. It shows how to:

- Read DICOM files using pydicom
- Extract patient information (name, ID, birth date, sex)
- Extract study details (description, date, time, UID)
- Extract series information (description, number, modality, UID)
- Extract image properties (dimensions, slice thickness, pixel spacing)
- Display information in a well-formatted, readable output

### How to Run

**Command:**
```bash
python examples/basic_dicom_info.py /path/to/dicom/file.dcm
```

**Example:**
```bash
python examples/basic_dicom_info.py ~/DICOM_Data/brain_mri_001.dcm
```

### Expected Output

```
DICOM Info Extractor - Example Script
======================================
Reading DICOM file: /path/to/brain_mri_001.dcm

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

Processing complete!
```

### Modification Tips

#### 1. Extract Additional DICOM Tags

Add more fields to the extraction dictionaries:

```python
# In extract_dicom_info function
patient_info = {
    'name': ds.get('PatientName', 'N/A'),
    'id': ds.get('PatientID', 'N/A'),
    'birth_date': ds.get('PatientBirthDate', 'N/A'),
    'sex': ds.get('PatientSex', 'N/A'),
    # Add these:
    'age': ds.get('PatientAge', 'N/A'),
    'weight': ds.get('PatientWeight', 'N/A'),
    'height': ds.get('PatientSize', 'N/A'),
}
```

#### 2. Export to JSON

Save extracted data for further processing:

```python
import json

def save_to_json(info, output_path):
    """Save DICOM info to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(info, f, indent=2, default=str)

# In main():
info = extract_dicom_info(dicom_path)
save_to_json(info, 'dicom_info.json')
```

#### 3. Filter Specific Modalities

Process only certain types of images:

```python
def extract_dicom_info(dicom_path, allowed_modalities=['MR', 'CT']):
    """Extract info only from specific modality types."""
    ds = pydicom.dcmread(dicom_path)

    modality = ds.get('Modality', 'N/A')
    if modality not in allowed_modalities:
        print(f"Skipping {modality} image")
        return None

    # Continue with extraction...
```

#### 4. Add Validation Checks

Verify DICOM data quality:

```python
def validate_dicom(ds):
    """Check for required DICOM tags."""
    required_tags = ['PatientID', 'StudyInstanceUID', 'SeriesInstanceUID']
    missing = [tag for tag in required_tags if tag not in ds]

    if missing:
        print(f"Warning: Missing required tags: {missing}")
        return False
    return True
```

---

## Example 2: Batch Processing

**File:** `examples/batch_processing.py`

### Overview

This example demonstrates professional batch processing of multiple DICOM files. It shows how to:

- Recursively find all DICOM files in a directory tree
- Process multiple files with progress reporting
- Handle errors gracefully without stopping the batch
- Group results by study UID
- Generate comprehensive summary reports with statistics
- Track success/failure rates

### How to Run

**Command:**
```bash
python examples/batch_processing.py /path/to/dicom/directory
```

**Example:**
```bash
python examples/batch_processing.py ~/DICOM_Data/Patient_Studies
```

### Expected Output

```
DICOM Batch Processor - Example Script
========================================

Searching for DICOM files in: /path/to/Patient_Studies
Found 150 DICOM files
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
```

### Modification Tips

#### 1. Add Custom Processing Logic

Replace the metadata extraction with your own processing:

```python
def process_single_image(dicom_path: Path) -> Tuple[bool, Dict]:
    """Your custom processing logic."""
    try:
        import pydicom
        ds = pydicom.dcmread(dicom_path)

        # Your custom processing here
        result = perform_custom_analysis(ds)

        return True, result
    except Exception as e:
        return False, {'error': str(e), 'filename': dicom_path.name}
```

#### 2. Parallel Processing

Use multiprocessing for faster batch operations:

```python
from multiprocessing import Pool, cpu_count

def process_batch_parallel(dicom_files):
    """Process files in parallel."""
    with Pool(cpu_count()) as pool:
        results = pool.map(process_single_image, dicom_files)
    return results

# In main():
results = process_batch_parallel(dicom_files)
```

#### 3. Filter by Date Range

Process only studies from specific time period:

```python
from datetime import datetime

def is_in_date_range(ds, start_date, end_date):
    """Check if study is within date range."""
    study_date_str = ds.get('StudyDate', '')
    if len(study_date_str) == 8:
        study_date = datetime.strptime(study_date_str, '%Y%m%d')
        return start_date <= study_date <= end_date
    return False

# In process_single_image():
if not is_in_date_range(ds, start_date, end_date):
    return False, {'skipped': 'Outside date range'}
```

#### 4. Export Results Database

Save all results to a SQLite database:

```python
import sqlite3

def create_results_db(results, db_path):
    """Store results in SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dicom_files (
            filename TEXT,
            patient_id TEXT,
            study_uid TEXT,
            series_number INTEGER,
            modality TEXT,
            study_description TEXT
        )
    ''')

    for success, result in results:
        if success:
            cursor.execute('''
                INSERT INTO dicom_files VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result['filename'],
                result['patient_id'],
                result['study_uid'],
                result['series_number'],
                result['modality'],
                result['study_description']
            ))

    conn.commit()
    conn.close()

# In main():
create_results_db(results, 'batch_results.db')
```

#### 5. Add Resume Capability

Support resuming interrupted batch jobs:

```python
import json
from pathlib import Path

def save_progress(processed_files, checkpoint_file):
    """Save list of processed files."""
    with open(checkpoint_file, 'w') as f:
        json.dump(processed_files, f)

def load_progress(checkpoint_file):
    """Load list of already processed files."""
    if Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r') as f:
            return set(json.load(f))
    return set()

# In main():
checkpoint = load_progress('batch_checkpoint.json')
processed_files = []

for idx, dicom_file in enumerate(dicom_files, start=1):
    if str(dicom_file) in checkpoint:
        print(f"Skipping already processed: {dicom_file.name}")
        continue

    # Process file...
    processed_files.append(str(dicom_file))

    # Save progress every 10 files
    if idx % 10 == 0:
        save_progress(processed_files, 'batch_checkpoint.json')
```

---

## Example 3: Custom Image Filters

**File:** `examples/custom_filter.py`

### Overview

This example demonstrates advanced image processing on DICOM pixel data. It shows how to:

- Load pixel arrays from DICOM files using NumPy
- Apply Gaussian blur filters for image smoothing
- Perform Sobel edge detection to highlight boundaries
- Enhance image contrast using percentile-based normalization
- Compute and display detailed image statistics
- Compare original and filtered images with quantitative metrics
- Use customizable filter parameters for different effects

### How to Run

**Command:**
```bash
python examples/custom_filter.py <path_to_dicom_file> [gaussian_sigma] [edge_sigma]
```

**Examples:**
```bash
# Basic usage with default parameters
python examples/custom_filter.py ~/DICOM_Data/brain_mri.dcm

# Custom Gaussian blur strength (stronger blur)
python examples/custom_filter.py ~/DICOM_Data/brain_mri.dcm 3.0

# Custom both Gaussian and edge detection parameters
python examples/custom_filter.py ~/DICOM_Data/brain_mri.dcm 2.5 1.5
```

**Parameters:**
- `path_to_dicom_file`: Path to DICOM file (required)
- `gaussian_sigma`: Blur strength (default: 2.0, range: 0.5-5.0)
- `edge_sigma`: Edge detection smoothing (default: 1.0, range: 0.5-2.0)

### Expected Output

```
Custom Image Filter - Example Script
=====================================

Loading DICOM file: /path/to/brain_mri.dcm

======================================================================
IMAGE METADATA
======================================================================
Dimensions:     512 x 512 pixels
Modality:       MR
Bits Allocated: 16
Pixel Spacing:  0.469 x 0.469 mm
======================================================================

[1] Gaussian Blur Filter
  Applying Gaussian filter (sigma=2.0)...

======================================================================
FILTER COMPARISON: Gaussian Blur
======================================================================

[Original Image]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  0.00
  Max Value:  4095.00
  Mean:       427.83
  Std Dev:    312.45
  Median:     385.00

[After Gaussian Blur]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  45.23
  Max Value:  3876.12
  Mean:       427.83
  Std Dev:    298.67
  Median:     385.42

[Changes]
  Mean change:   +0.00%
  Std Dev change: -4.41%

======================================================================

[2] Edge Detection Filter
  Applying edge detection (sigma=1.0)...

======================================================================
FILTER COMPARISON: Edge Detection
======================================================================

[Original Image]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  0.00
  Max Value:  4095.00
  Mean:       427.83
  Std Dev:    312.45
  Median:     385.00

[After Edge Detection]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  0.00
  Max Value:  892.34
  Mean:       24.56
  Std Dev:    48.92
  Median:     8.73

[Changes]
  Mean change:   -94.26%
  Std Dev change: -84.34%

======================================================================

[3] Contrast Enhancement
  Enhancing contrast (p2.0-p98.0)...

======================================================================
FILTER COMPARISON: Contrast Enhancement
======================================================================

[Original Image]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  0.00
  Max Value:  4095.00
  Mean:       427.83
  Std Dev:    312.45
  Median:     385.00

[After Contrast Enhancement]
  Shape:      (512, 512)
  Data Type:  float64
  Min Value:  0.00
  Max Value:  1.00
  Mean:       0.47
  Std Dev:    0.28
  Median:     0.45

[Changes]
  Mean change:   -99.89%
  Std Dev change: -99.91%

======================================================================

======================================================================
PROCESSING SUMMARY
======================================================================
Original image shape:     (512, 512)
Filters applied:          3
Gaussian sigma used:      2.0
Edge detection sigma:     1.0
Contrast enhancement:     Enabled

All filters processed successfully!
======================================================================

Processing complete!
```

### Modification Tips

#### 1. Add More Filter Types

Implement additional image processing filters:

```python
from scipy.ndimage import median_filter, uniform_filter

def apply_median_filter(image: np.ndarray, size: int = 3) -> np.ndarray:
    """Apply median filter to reduce noise."""
    print(f"  Applying median filter (size={size})...", flush=True)
    filtered = median_filter(image, size=size)
    return filtered

def apply_sharpening(image: np.ndarray, alpha: float = 1.5) -> np.ndarray:
    """Sharpen image by subtracting blurred version."""
    print(f"  Applying sharpening filter (alpha={alpha})...", flush=True)
    blurred = gaussian_filter(image, sigma=1.0)
    sharpened = image + alpha * (image - blurred)
    return sharpened
```

#### 2. Save Filtered Images

Export processed images as new DICOM files:

```python
def save_filtered_dicom(original_ds, filtered_array, output_path):
    """Save filtered image as new DICOM file."""
    import pydicom

    # Create a copy of the original dataset
    new_ds = original_ds.copy()

    # Update pixel data with filtered array
    new_ds.PixelData = filtered_array.astype(np.uint16).tobytes()

    # Update series description
    new_ds.SeriesDescription = f"{new_ds.SeriesDescription} - Filtered"

    # Save the new DICOM file
    new_ds.save_as(output_path)
    print(f"Saved filtered image to: {output_path}")

# In main():
ds = pydicom.dcmread(dicom_path)
filtered = apply_gaussian_filter(pixel_data, sigma=2.0)
save_filtered_dicom(ds, filtered, 'filtered_output.dcm')
```

#### 3. Visualize Results

Create comparison images (requires matplotlib):

```python
import matplotlib.pyplot as plt

def visualize_filters(original, gaussian, edges, contrast):
    """Display original and filtered images side by side."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))

    axes[0, 0].imshow(original, cmap='gray')
    axes[0, 0].set_title('Original')

    axes[0, 1].imshow(gaussian, cmap='gray')
    axes[0, 1].set_title('Gaussian Blur')

    axes[1, 0].imshow(edges, cmap='gray')
    axes[1, 0].set_title('Edge Detection')

    axes[1, 1].imshow(contrast, cmap='gray')
    axes[1, 1].set_title('Contrast Enhanced')

    plt.tight_layout()
    plt.savefig('filter_comparison.png', dpi=150)
    print("Saved visualization to: filter_comparison.png")

# In process_with_filters():
visualize_filters(pixel_data, gaussian_filtered, edge_filtered, contrast_enhanced)
```

#### 4. Create Custom Filter Pipelines

Chain multiple filters together:

```python
def apply_filter_pipeline(image: np.ndarray, pipeline_config: Dict) -> np.ndarray:
    """Apply a sequence of filters based on configuration."""
    result = image.copy()

    for step in pipeline_config['steps']:
        filter_type = step['type']
        params = step['params']

        if filter_type == 'gaussian':
            result = apply_gaussian_filter(result, **params)
        elif filter_type == 'edge':
            result = apply_edge_detection(result, **params)
        elif filter_type == 'contrast':
            result = apply_contrast_enhancement(result, **params)
        # Add more filter types...

    return result

# Example usage:
pipeline = {
    'steps': [
        {'type': 'gaussian', 'params': {'sigma': 1.0}},
        {'type': 'contrast', 'params': {'percentile_low': 5, 'percentile_high': 95}},
        {'type': 'edge', 'params': {'sigma': 0.5}}
    ]
}

filtered = apply_filter_pipeline(pixel_data, pipeline)
```

#### 5. Batch Filter Application

Apply filters to multiple files:

```python
def batch_filter_directory(directory: Path, output_dir: Path, filter_func):
    """Apply filter to all DICOM files in a directory."""
    from pathlib import Path

    output_dir.mkdir(exist_ok=True)
    dicom_files = list(directory.glob('*.dcm'))

    for idx, dicom_file in enumerate(dicom_files, 1):
        print(f"[{idx}/{len(dicom_files)}] Processing: {dicom_file.name}")

        pixel_data, metadata = load_dicom_pixel_data(dicom_file)
        if pixel_data is not None:
            filtered = filter_func(pixel_data)

            # Save with same filename in output directory
            output_path = output_dir / dicom_file.name
            save_filtered_dicom(dicom_file, filtered, output_path)

# Usage:
batch_filter_directory(
    Path('input_dicoms'),
    Path('filtered_output'),
    lambda img: apply_gaussian_filter(img, sigma=2.0)
)
```

#### 6. Add Region of Interest (ROI) Processing

Process specific regions of the image:

```python
def apply_filter_to_roi(image: np.ndarray, filter_func,
                        x: int, y: int, width: int, height: int) -> np.ndarray:
    """Apply filter only to a specific region."""
    result = image.copy()

    # Extract ROI
    roi = image[y:y+height, x:x+width]

    # Apply filter to ROI
    filtered_roi = filter_func(roi)

    # Place filtered ROI back
    result[y:y+height, x:x+width] = filtered_roi

    return result

# Usage:
filtered = apply_filter_to_roi(
    pixel_data,
    lambda img: apply_gaussian_filter(img, sigma=3.0),
    x=100, y=100, width=200, height=200
)
```

---

## General Tips

### 1. Error Handling Best Practices

All examples include robust error handling:

```python
try:
    # Your processing code
    result = process_dicom(path)
except FileNotFoundError:
    print(f"Error: File not found: {path}", file=sys.stderr)
except Exception as e:
    print(f"Error processing file: {e}", file=sys.stderr)
```

### 2. Output Flushing

Use `flush=True` for immediate output visibility in Xcode console:

```python
print("Processing...", flush=True)
```

### 3. Memory Management

For large datasets, process files one at a time:

```python
# Good: Process one file at a time
for dicom_file in dicom_files:
    pixel_data = load_dicom(dicom_file)
    process(pixel_data)
    del pixel_data  # Free memory

# Bad: Load all files into memory
all_data = [load_dicom(f) for f in dicom_files]  # Can run out of memory!
```

### 4. Progress Reporting

Keep users informed during long operations:

```python
total = len(files)
for idx, file in enumerate(files, 1):
    percentage = (idx / total) * 100
    print(f"[{idx}/{total}] ({percentage:.1f}%) Processing: {file.name}")
```

### 5. Testing Scripts Standalone

Test scripts independently before plugin integration:

```bash
# Test with a single file
python examples/basic_dicom_info.py test_data/sample.dcm

# Test with a directory
python examples/batch_processing.py test_data/

# Test with custom parameters
python examples/custom_filter.py test_data/sample.dcm 2.5 1.0
```

---

## Integrating Examples into Your Plugin

### Step 1: Choose Your Base Example

Select the example that matches your use case:

- **Single file processing** → Use `basic_dicom_info.py`
- **Multiple file processing** → Use `batch_processing.py`
- **Image manipulation** → Use `custom_filter.py`

### Step 2: Modify Plugin.swift

Update your plugin to pass DICOM paths:

```swift
// In Plugin.swift
func run() {
    let selectedImages = viewerController.imageView.dcmPixList

    for image in selectedImages {
        if let dicomPath = image.completePath {
            // Pass path to Python script
            let args = [dicomPath]
            let result = pythonRunner.runScript("main.py", arguments: args)
            print(result)
        }
    }
}
```

### Step 3: Replace main.py

Copy your chosen example as the new main.py:

```bash
cp examples/basic_dicom_info.py python_scripts/main.py
```

### Step 4: Customize Logic

Modify the script's processing logic for your specific needs (see modification tips above).

### Step 5: Test in OsiriX/Horos

1. Build and run the plugin in Xcode
2. Open a DICOM study in OsiriX/Horos
3. Run your plugin from the Plugins menu
4. Check output in Xcode console

### Example Integration

Here's a complete example integrating the batch processor:

```python
# Custom main.py based on batch_processing.py

import sys
from pathlib import Path

def process_image_from_plugin(dicom_path):
    """Process a single image called from the plugin."""
    # Your custom processing logic
    result = extract_features(dicom_path)

    # Return result to plugin
    print(f"RESULT:{result}", flush=True)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No DICOM path provided", file=sys.stderr)
        sys.exit(1)

    dicom_path = Path(sys.argv[1])
    process_image_from_plugin(dicom_path)
```

---

## Additional Resources

- [PyDICOM Documentation](https://pydicom.github.io/)
- [NumPy User Guide](https://numpy.org/doc/stable/user/)
- [SciPy ndimage Reference](https://docs.scipy.org/doc/scipy/reference/ndimage.html)
- [DICOM Standard](https://www.dicomstandard.org/)

## Getting Help

If you encounter issues:

1. Check that all dependencies are installed
2. Verify DICOM files are valid (not corrupted)
3. Test scripts standalone before plugin integration
4. Check Xcode console for error messages
5. Review the [API Documentation](API.md) for plugin integration details

---

**Last Updated:** February 2026
**Author:** Thales Matheus Mendonca Santos
