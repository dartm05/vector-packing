#!/bin/bash
# Download Azure Packing Trace 2020 Dataset
# This script downloads the dataset needed for Azure data experiments

set -e  # Exit on error

echo "=============================================================================="
echo "Azure Packing Trace 2020 - Dataset Downloader"
echo "=============================================================================="
echo ""
echo "This script will download the Microsoft Azure VM allocation dataset"
echo "Source: Azure Public Dataset (OSDI 2020 - Protean paper)"
echo "License: CC-BY Attribution"
echo ""
echo "Download size: ~51 MB"
echo "Extracted size: ~173 MB"
echo ""
echo "=============================================================================="
echo ""

# Create datasets directory if it doesn't exist
mkdir -p datasets

# Check if dataset already exists
if [ -f "datasets/packing_trace_zone_a_v1.sqlite" ]; then
    echo "✓ Dataset already exists!"
    echo ""
    echo "Location: datasets/packing_trace_zone_a_v1.sqlite"
    echo "Size: $(du -h datasets/packing_trace_zone_a_v1.sqlite | cut -f1)"
    echo ""
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Skipping download. Dataset ready to use!"
        exit 0
    fi
    echo ""
    echo "Re-downloading dataset..."
fi

# Download the dataset
echo "Step 1/2: Downloading Azure Packing Trace (this may take 30-60 seconds)..."
echo ""

cd datasets

curl -L -o AzurePackingTraceV1.zip \
    "https://azurepublicdatasettraces.blob.core.windows.net/azurepublicdatasetv2/azurevmallocation_dataset2020/AzurePackingTraceV1.zip"

echo ""
echo "✓ Download complete!"
echo ""

# Extract the dataset
echo "Step 2/2: Extracting dataset..."
echo ""

unzip -o AzurePackingTraceV1.zip

echo ""
echo "✓ Extraction complete!"
echo ""

# Cleanup
echo "Cleaning up..."
rm AzurePackingTraceV1.zip

cd ..

# Verify
echo ""
echo "=============================================================================="
echo "✓ DATASET READY!"
echo "=============================================================================="
echo ""
echo "Location: datasets/packing_trace_zone_a_v1.sqlite"
echo "Size: $(du -h datasets/packing_trace_zone_a_v1.sqlite | cut -f1)"
echo ""
echo "Quick Test:"
echo "  python3 test_azure_loader.py"
echo ""
echo "Use in GUI:"
echo "  python3 gui.py"
echo "  Then select 'azure' from Data Source dropdown"
echo ""
echo "Documentation:"
echo "  AZURE_DATASET.md       - Complete dataset documentation"
echo "  QUICK_START_AZURE.md   - Quick start guide"
echo "  GUI_AZURE_GUIDE.md     - GUI usage guide"
echo ""
echo "=============================================================================="
