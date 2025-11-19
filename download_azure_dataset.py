#!/usr/bin/env python3
"""
Azure Packing Trace 2020 - Dataset Downloader

This script downloads the Microsoft Azure VM allocation dataset
needed for Azure data experiments.

Source: Azure Public Dataset (OSDI 2020 - Protean paper)
License: CC-BY Attribution
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path


def print_header():
    """Print header information"""
    print("=" * 78)
    print("Azure Packing Trace 2020 - Dataset Downloader")
    print("=" * 78)
    print()
    print("This script will download the Microsoft Azure VM allocation dataset")
    print("Source: Azure Public Dataset (OSDI 2020 - Protean paper)")
    print("License: CC-BY Attribution")
    print()
    print("Download size: ~51 MB")
    print("Extracted size: ~173 MB")
    print()
    print("=" * 78)
    print()


def check_existing_dataset():
    """Check if dataset already exists"""
    dataset_path = Path("datasets/packing_trace_zone_a_v1.sqlite")

    if dataset_path.exists():
        size_mb = dataset_path.stat().st_size / (1024 * 1024)
        print(f"✓ Dataset already exists!")
        print()
        print(f"Location: {dataset_path}")
        print(f"Size: {size_mb:.1f} MB")
        print()

        response = input("Do you want to re-download? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print()
            print("Skipping download. Dataset ready to use!")
            return True

        print()
        print("Re-downloading dataset...")
        print()

    return False


def download_file(url, destination):
    """Download file with progress indicator"""

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 / total_size)
        bar_length = 50
        filled_length = int(bar_length * downloaded // total_size)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)

        print(f"\r  [{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
              end='', flush=True)

    print(f"Downloading from: {url}")
    print()

    try:
        urllib.request.urlretrieve(url, destination, reporthook=report_progress)
        print()  # New line after progress bar
        print()
        return True
    except Exception as e:
        print()
        print(f"✗ Error downloading: {e}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file"""
    print("Extracting dataset...")
    print()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"✗ Error extracting: {e}")
        return False


def cleanup(zip_path):
    """Remove zip file after extraction"""
    try:
        if Path(zip_path).exists():
            os.remove(zip_path)
    except Exception as e:
        print(f"Warning: Could not remove zip file: {e}")


def verify_dataset():
    """Verify dataset was downloaded successfully"""
    dataset_path = Path("datasets/packing_trace_zone_a_v1.sqlite")

    if not dataset_path.exists():
        print("✗ Dataset file not found after extraction!")
        print(f"Expected: {dataset_path}")
        return False

    size_mb = dataset_path.stat().st_size / (1024 * 1024)

    if size_mb < 100:
        print(f"✗ Dataset file seems too small ({size_mb:.1f} MB)")
        print("Expected: ~173 MB")
        return False

    return True


def print_success():
    """Print success message"""
    dataset_path = Path("datasets/packing_trace_zone_a_v1.sqlite")
    size_mb = dataset_path.stat().st_size / (1024 * 1024)

    print()
    print("=" * 78)
    print("✓ DATASET READY!")
    print("=" * 78)
    print()
    print(f"Location: {dataset_path}")
    print(f"Size: {size_mb:.1f} MB")
    print()
    print("Quick Test:")
    print("  python3 test_azure_loader.py")
    print()
    print("Use in GUI:")
    print("  python3 gui.py")
    print("  Then select 'azure' from Data Source dropdown")
    print()
    print("Documentation:")
    print("  AZURE_DATASET.md       - Complete dataset documentation")
    print("  QUICK_START_AZURE.md   - Quick start guide")
    print("  GUI_AZURE_GUIDE.md     - GUI usage guide")
    print()
    print("=" * 78)


def main():
    """Main download process"""
    print_header()

    # Create datasets directory
    Path("datasets").mkdir(exist_ok=True)

    # Check if dataset exists
    if check_existing_dataset():
        return 0

    # Download URL
    url = "https://azurepublicdatasettraces.blob.core.windows.net/azurepublicdatasetv2/azurevmallocation_dataset2020/AzurePackingTraceV1.zip"
    zip_path = "datasets/AzurePackingTraceV1.zip"

    # Download
    print("Step 1/2: Downloading Azure Packing Trace")
    print("(This may take 30-60 seconds depending on your connection)")
    print()

    if not download_file(url, zip_path):
        print()
        print("✗ Download failed!")
        print()
        print("You can try downloading manually from:")
        print(url)
        print()
        print(f"Save as: {zip_path}")
        print("Then run this script again to extract.")
        return 1

    print("✓ Download complete!")
    print()

    # Extract
    print("Step 2/2: Extracting dataset...")
    print()

    if not extract_zip(zip_path, "datasets"):
        print()
        print("✗ Extraction failed!")
        return 1

    print("✓ Extraction complete!")
    print()

    # Cleanup
    print("Cleaning up...")
    cleanup(zip_path)
    print("✓ Cleanup complete!")

    # Verify
    if not verify_dataset():
        print()
        print("✗ Dataset verification failed!")
        return 1

    # Success
    print_success()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print()
        print("Download cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
