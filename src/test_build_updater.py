"""
Quick test script to build updater.exe
"""

from pathlib import Path
from updater.updater_builder import UpdaterBuilder

# Test configuration
url = "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app"
source_type = "GitHub Network (Assets)"
save_dir = Path(r"C:\Users\Vitalii\Documents\vscode-workflow\ultimate-updater\auto-updater\src\dist\test_updater")

# Sample metadata (from previous download)
sha256 = "eae9f6c747b8532ed92058ae66251aae4efc5aa3a64590baed39b711b496677c"
release_date = "2025-11-08T11:32:44Z"
target_filename = "main.exe"

print("Building updater.exe...")
print(f"URL: {url}")
print(f"Source: {source_type}")
print(f"Directory: {save_dir}")

builder = UpdaterBuilder(save_dir)
result = builder.build(
    source_type=source_type,
    url=url,
    sha256=sha256,
    release_date=release_date,
    target_filename=target_filename
)

if result:
    print(f"\n✓ Success! Created: {result}")
    print("\nTo test, run:")
    print(f"  {result}")
else:
    print("\n✗ Build failed")
