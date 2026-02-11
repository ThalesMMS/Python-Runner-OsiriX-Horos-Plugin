#!/usr/bin/env python3
#
# custom_filter.py
# PythonRunner Example Script
#
# Demonstrates custom image filtering and manipulation on DICOM images.
# This example shows how to apply image processing filters (Gaussian blur,
# edge detection, contrast enhancement) using numpy and scipy, and display
# results with customizable filter parameters.
#
# Thales Matheus Mendonca Santos - January 2026
#

import sys
from pathlib import Path
from typing import Tuple, Dict, Optional
import numpy as np


def load_dicom_pixel_data(dicom_path: Path) -> Tuple[Optional[np.ndarray], Dict]:
    """
    Load pixel data from a DICOM file.

    Args:
        dicom_path: Path to the DICOM file

    Returns:
        Tuple of (pixel_array, metadata)
        - pixel_array: NumPy array of pixel data or None if loading failed
        - metadata: Dictionary containing image metadata
    """
    try:
        import pydicom
    except ImportError:
        print("Error: pydicom is not installed.", file=sys.stderr, flush=True)
        print("Install with: pip install pydicom", file=sys.stderr, flush=True)
        return None, {'error': 'pydicom not installed'}

    try:
        # Read the DICOM file
        ds = pydicom.dcmread(dicom_path)

        # Get pixel array
        pixel_array = ds.pixel_array.astype(float)

        # Extract metadata
        metadata = {
            'rows': ds.Rows,
            'columns': ds.Columns,
            'modality': ds.get('Modality', 'N/A'),
            'bits_allocated': ds.get('BitsAllocated', 'N/A'),
            'pixel_spacing': ds.get('PixelSpacing', [1.0, 1.0]),
            'window_center': ds.get('WindowCenter', None),
            'window_width': ds.get('WindowWidth', None),
        }

        return pixel_array, metadata

    except Exception as e:
        print(f"Error loading DICOM pixel data: {e}", file=sys.stderr, flush=True)
        return None, {'error': str(e)}


def apply_gaussian_filter(image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    Apply Gaussian blur filter to smooth the image.

    Args:
        image: Input image as NumPy array
        sigma: Standard deviation for Gaussian kernel (larger = more blur)

    Returns:
        Filtered image as NumPy array
    """
    try:
        from scipy.ndimage import gaussian_filter
    except ImportError:
        print("Error: scipy is not installed.", file=sys.stderr, flush=True)
        print("Install with: pip install scipy", file=sys.stderr, flush=True)
        sys.exit(1)

    print(f"  Applying Gaussian filter (sigma={sigma})...", flush=True)
    filtered = gaussian_filter(image, sigma=sigma)
    return filtered


def apply_edge_detection(image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    Apply Sobel edge detection filter to highlight edges.

    Args:
        image: Input image as NumPy array
        sigma: Standard deviation for Gaussian smoothing before edge detection

    Returns:
        Edge-detected image as NumPy array
    """
    try:
        from scipy.ndimage import sobel, gaussian_filter
    except ImportError:
        print("Error: scipy is not installed.", file=sys.stderr, flush=True)
        print("Install with: pip install scipy", file=sys.stderr, flush=True)
        sys.exit(1)

    print(f"  Applying edge detection (sigma={sigma})...", flush=True)

    # Smooth first to reduce noise
    smoothed = gaussian_filter(image, sigma=sigma)

    # Compute gradients in x and y directions
    gradient_x = sobel(smoothed, axis=0)
    gradient_y = sobel(smoothed, axis=1)

    # Compute magnitude of gradient
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)

    return magnitude


def apply_contrast_enhancement(image: np.ndarray, percentile_low: float = 2.0,
                               percentile_high: float = 98.0) -> np.ndarray:
    """
    Enhance image contrast using percentile-based normalization.

    Args:
        image: Input image as NumPy array
        percentile_low: Lower percentile for normalization (default: 2.0)
        percentile_high: Upper percentile for normalization (default: 98.0)

    Returns:
        Contrast-enhanced image as NumPy array
    """
    print(f"  Enhancing contrast (p{percentile_low}-p{percentile_high})...", flush=True)

    # Calculate percentiles
    p_low = np.percentile(image, percentile_low)
    p_high = np.percentile(image, percentile_high)

    # Clip and normalize to [0, 1]
    enhanced = np.clip(image, p_low, p_high)
    enhanced = (enhanced - p_low) / (p_high - p_low)

    return enhanced


def compute_image_statistics(image: np.ndarray) -> Dict:
    """
    Compute statistical properties of the image.

    Args:
        image: Input image as NumPy array

    Returns:
        Dictionary containing image statistics
    """
    stats = {
        'min': np.min(image),
        'max': np.max(image),
        'mean': np.mean(image),
        'std': np.std(image),
        'median': np.median(image),
        'shape': image.shape,
        'dtype': str(image.dtype),
    }
    return stats


def display_statistics(title: str, stats: Dict):
    """
    Display image statistics in a formatted output.

    Args:
        title: Title for the statistics section
        stats: Dictionary containing image statistics
    """
    print(f"\n[{title}]", flush=True)
    print(f"  Shape:      {stats['shape']}", flush=True)
    print(f"  Data Type:  {stats['dtype']}", flush=True)
    print(f"  Min Value:  {stats['min']:.2f}", flush=True)
    print(f"  Max Value:  {stats['max']:.2f}", flush=True)
    print(f"  Mean:       {stats['mean']:.2f}", flush=True)
    print(f"  Std Dev:    {stats['std']:.2f}", flush=True)
    print(f"  Median:     {stats['median']:.2f}", flush=True)


def display_filter_comparison(original_stats: Dict, filtered_stats: Dict,
                              filter_name: str):
    """
    Display a comparison between original and filtered images.

    Args:
        original_stats: Statistics of the original image
        filtered_stats: Statistics of the filtered image
        filter_name: Name of the applied filter
    """
    print("\n" + "="*70, flush=True)
    print(f"FILTER COMPARISON: {filter_name}", flush=True)
    print("="*70, flush=True)

    display_statistics("Original Image", original_stats)
    display_statistics(f"After {filter_name}", filtered_stats)

    # Calculate changes
    mean_change = ((filtered_stats['mean'] - original_stats['mean'])
                   / original_stats['mean'] * 100)
    std_change = ((filtered_stats['std'] - original_stats['std'])
                  / original_stats['std'] * 100)

    print("\n[Changes]", flush=True)
    print(f"  Mean change:   {mean_change:+.2f}%", flush=True)
    print(f"  Std Dev change: {std_change:+.2f}%", flush=True)

    print("="*70, flush=True)


def process_with_filters(dicom_path: Path, gaussian_sigma: float = 2.0,
                        edge_sigma: float = 1.0, enable_contrast: bool = True):
    """
    Process a DICOM image with multiple filters and display results.

    Args:
        dicom_path: Path to the DICOM file
        gaussian_sigma: Sigma parameter for Gaussian blur
        edge_sigma: Sigma parameter for edge detection
        enable_contrast: Whether to apply contrast enhancement
    """
    print(f"\nLoading DICOM file: {dicom_path}", flush=True)

    # Load pixel data
    pixel_data, metadata = load_dicom_pixel_data(dicom_path)

    if pixel_data is None:
        print("Failed to load pixel data", file=sys.stderr, flush=True)
        return

    # Display image metadata
    print("\n" + "="*70, flush=True)
    print("IMAGE METADATA", flush=True)
    print("="*70, flush=True)
    print(f"Dimensions:     {metadata['rows']} x {metadata['columns']} pixels", flush=True)
    print(f"Modality:       {metadata['modality']}", flush=True)
    print(f"Bits Allocated: {metadata['bits_allocated']}", flush=True)

    spacing = metadata['pixel_spacing']
    if isinstance(spacing, list) and len(spacing) == 2:
        print(f"Pixel Spacing:  {spacing[0]:.3f} x {spacing[1]:.3f} mm", flush=True)

    print("="*70, flush=True)

    # Compute original statistics
    original_stats = compute_image_statistics(pixel_data)

    # Apply Gaussian filter
    print("\n[1] Gaussian Blur Filter", flush=True)
    gaussian_filtered = apply_gaussian_filter(pixel_data, sigma=gaussian_sigma)
    gaussian_stats = compute_image_statistics(gaussian_filtered)
    display_filter_comparison(original_stats, gaussian_stats, "Gaussian Blur")

    # Apply edge detection
    print("\n[2] Edge Detection Filter", flush=True)
    edge_filtered = apply_edge_detection(pixel_data, sigma=edge_sigma)
    edge_stats = compute_image_statistics(edge_filtered)
    display_filter_comparison(original_stats, edge_stats, "Edge Detection")

    # Apply contrast enhancement
    if enable_contrast:
        print("\n[3] Contrast Enhancement", flush=True)
        contrast_enhanced = apply_contrast_enhancement(pixel_data)
        contrast_stats = compute_image_statistics(contrast_enhanced)
        display_filter_comparison(original_stats, contrast_stats,
                                "Contrast Enhancement")

    # Display summary
    print("\n" + "="*70, flush=True)
    print("PROCESSING SUMMARY", flush=True)
    print("="*70, flush=True)
    print(f"Original image shape:     {original_stats['shape']}", flush=True)
    print(f"Filters applied:          3", flush=True)
    print(f"Gaussian sigma used:      {gaussian_sigma}", flush=True)
    print(f"Edge detection sigma:     {edge_sigma}", flush=True)
    print(f"Contrast enhancement:     {'Enabled' if enable_contrast else 'Disabled'}", flush=True)
    print("\nAll filters processed successfully!", flush=True)
    print("="*70, flush=True)


def main():
    """
    Main entry point for the custom image filtering script.

    This script demonstrates how to:
    - Load and manipulate DICOM pixel data using NumPy
    - Apply image processing filters (Gaussian, edge detection, contrast)
    - Use scipy.ndimage for advanced filtering operations
    - Compute and display image statistics
    - Compare original and filtered images
    - Customize filter parameters for different effects

    Usage:
        python custom_filter.py <path_to_dicom_file> [gaussian_sigma] [edge_sigma]

    Arguments:
        path_to_dicom_file: Path to the DICOM file to process (required)
        gaussian_sigma:     Sigma for Gaussian blur (default: 2.0)
        edge_sigma:         Sigma for edge detection (default: 1.0)

    Examples:
        # Basic usage with default parameters
        python custom_filter.py /path/to/image.dcm

        # Custom Gaussian blur strength
        python custom_filter.py /path/to/image.dcm 3.0

        # Custom both Gaussian and edge detection sigma
        python custom_filter.py /path/to/image.dcm 2.5 1.5

    Example Output:
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

    Notes:
        - Larger sigma values create stronger blur and smoother edges
        - Edge detection works best with moderate smoothing (sigma 0.5-2.0)
        - Contrast enhancement normalizes the intensity range
        - All operations preserve the original image data
        - This demonstrates the core concepts for custom filter development
    """
    # Keep output immediate so it shows up in the Xcode console
    print("Custom Image Filter - Example Script", flush=True)
    print("=====================================", flush=True)

    # Check for required dependencies
    try:
        import pydicom
        import scipy
    except ImportError as e:
        print(f"\nError: Required package not installed: {e}", file=sys.stderr, flush=True)
        print("\nInstall dependencies with:", flush=True)
        print("  pip install pydicom scipy numpy", flush=True)
        print("\nNote: This is a demonstration script showing image filtering.", flush=True)
        print("To use this in your plugin:", flush=True)
        print("  1. Install pydicom, scipy, and numpy in your virtual environment", flush=True)
        print("  2. Modify Plugin.swift to pass DICOM file paths as arguments", flush=True)
        print("  3. Adapt these filtering techniques for your image processing needs", flush=True)
        print("  4. Consider saving filtered results or passing them back to OsiriX/Horos", flush=True)
        sys.exit(1)

    # Check if a DICOM file path was provided
    if len(sys.argv) < 2:
        print("\nUsage: python custom_filter.py <path_to_dicom_file> [gaussian_sigma] [edge_sigma]", flush=True)
        print("\nArguments:", flush=True)
        print("  path_to_dicom_file: Path to the DICOM file (required)", flush=True)
        print("  gaussian_sigma:     Sigma for Gaussian blur (default: 2.0)", flush=True)
        print("  edge_sigma:         Sigma for edge detection (default: 1.0)", flush=True)
        print("\nThis script demonstrates:", flush=True)
        print("  - Loading DICOM pixel data with NumPy", flush=True)
        print("  - Applying Gaussian blur filter", flush=True)
        print("  - Applying Sobel edge detection", flush=True)
        print("  - Performing contrast enhancement", flush=True)
        print("  - Computing and comparing image statistics", flush=True)
        print("  - Using customizable filter parameters", flush=True)
        sys.exit(0)

    # Get the DICOM file path from command line arguments
    dicom_path = Path(sys.argv[1])

    # Parse optional filter parameters
    gaussian_sigma = 2.0
    edge_sigma = 1.0

    if len(sys.argv) >= 3:
        try:
            gaussian_sigma = float(sys.argv[2])
        except ValueError:
            print(f"Warning: Invalid gaussian_sigma '{sys.argv[2]}', using default 2.0",
                  file=sys.stderr, flush=True)

    if len(sys.argv) >= 4:
        try:
            edge_sigma = float(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid edge_sigma '{sys.argv[3]}', using default 1.0",
                  file=sys.stderr, flush=True)

    # Validate the file exists
    if not dicom_path.exists():
        print(f"Error: File does not exist: {dicom_path}", file=sys.stderr, flush=True)
        sys.exit(1)

    # Process the image with filters
    process_with_filters(dicom_path, gaussian_sigma, edge_sigma, enable_contrast=True)

    print("\nProcessing complete!", flush=True)


if __name__ == "__main__":
    # Explicit entrypoint for direct execution
    main()
