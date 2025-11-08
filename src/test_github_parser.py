"""
Example script demonstrating the GitHub Network (Assets) parsing functionality
"""

from updater.github_parser import GitHubParser
from utils.hash_utils import calculate_sha256
from datetime import datetime

def test_github_network_parsing():
    """Test parsing GitHub release page for .exe files"""
    
    # Example: Parse a GitHub release page
    repo_url = "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app"
    
    print("=" * 60)
    print("GitHub Network (Assets) Parsing Test")
    print("=" * 60)
    print(f"\nParsing: {repo_url}\n")
    
    parser = GitHubParser(repo_url)
    
    # Parse the network page for .exe files
    exe_files = parser.parse_network_page()
    
    if exe_files:
        print(f"Found {len(exe_files)} executable file(s):\n")
        
        for i, exe_info in enumerate(exe_files, 1):
            print(f"File #{i}:")
            print(f"  Filename:     {exe_info.get('filename', 'N/A')}")
            print(f"  Download URL: {exe_info.get('download_url', 'N/A')}")
            print(f"  SHA256:       {exe_info.get('sha256', 'N/A')}")
            print(f"  Release Date: {exe_info.get('release_date', 'N/A')}")
            print(f"  File Size:    {exe_info.get('file_size', 'N/A')}")
            print()
    else:
        print("No executable files found on the release page.")
    
    print("=" * 60)

def test_update_checking():
    """Test the update checking logic"""
    
    print("\n" + "=" * 60)
    print("Update Checking Test")
    print("=" * 60)
    
    repo_url = "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app"
    parser = GitHubParser(repo_url)
    
    # Simulate local file info
    local_sha256 = "old_hash_value_12345"
    local_date = datetime(2025, 11, 1)  # Older date
    
    print(f"\nLocal file info:")
    print(f"  SHA256: {local_sha256}")
    print(f"  Date:   {local_date}")
    
    # Check for updates
    needs_update, update_info = parser.check_for_updates_network(local_sha256, local_date)
    
    if needs_update:
        print(f"\n✓ Update available!")
        print(f"\nNew version info:")
        print(f"  Filename:     {update_info.get('filename', 'N/A')}")
        print(f"  SHA256:       {update_info.get('sha256', 'N/A')}")
        print(f"  Release Date: {update_info.get('release_date', 'N/A')}")
        print(f"  Download URL: {update_info.get('download_url', 'N/A')}")
    else:
        print(f"\n✗ No update needed - you have the latest version!")
    
    print("=" * 60)

def test_hash_calculation():
    """Test SHA256 hash calculation utilities"""
    
    print("\n" + "=" * 60)
    print("SHA256 Hash Utilities Test")
    print("=" * 60)
    
    # Note: This requires an actual file to test
    # For demonstration purposes only
    
    print("\nHash utility functions available:")
    print("  • calculate_sha256(file_path)")
    print("  • verify_file_hash(file_path, expected_hash)")
    print("  • get_file_metadata(file_path)")
    
    print("\nExample usage:")
    print("  hash = calculate_sha256('main.exe')")
    print("  is_valid = verify_file_hash('main.exe', 'sha256:abc123...')")
    
    print("=" * 60)

if __name__ == "__main__":
    print("\n🔍 Auto-Updater GitHub Network Parser - Test Suite\n")
    
    try:
        # Test 1: Parse GitHub release page
        test_github_network_parsing()
        
        # Test 2: Check for updates
        test_update_checking()
        
        # Test 3: Hash utilities info
        test_hash_calculation()
        
        print("\n✓ All tests completed!\n")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}\n")
        import traceback
        traceback.print_exc()
