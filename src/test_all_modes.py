"""
Test all three update modes with the fixed expanded_assets endpoint
"""

from updater.github_parser import GitHubParser

print("\n" + "=" * 70)
print("AUTO-UPDATER - Testing All Update Modes")
print("=" * 70)

# Test URL
test_url = "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app"

# Test 1: GitHub Release mode
print("\n" + "=" * 70)
print("TEST 1: GitHub Release Mode")
print("=" * 70)

parser1 = GitHubParser(test_url)
print(f"Regular URL: {parser1.releases_url}")
print(f"Expanded URL: {parser1.expanded_assets_url}")

result1 = parser1.get_latest_exe_info()

if result1:
    print("\n✅ SUCCESS!")
    print(f"  Filename: {result1['filename']}")
    print(f"  Download: {result1['download_url']}")
    sha256 = result1.get('sha256', 'N/A')
    if sha256 and sha256 != 'N/A':
        print(f"  SHA256: {sha256[:32]}...")
    else:
        print(f"  SHA256: {sha256}")
    print(f"  Date: {result1.get('release_date', 'N/A')}")
    print(f"  Size: {result1.get('file_size', 'N/A')}")
else:
    print("\n❌ FAILED - No .exe found")

# Test 2: GitHub Network (Assets) mode
print("\n" + "=" * 70)
print("TEST 2: GitHub Network (Assets) Mode")
print("=" * 70)

parser2 = GitHubParser(test_url)
result2 = parser2.parse_network_page()

if result2:
    print(f"\n✅ SUCCESS! Found {len(result2)} file(s)")
    for i, exe in enumerate(result2, 1):
        print(f"\nFile #{i}:")
        print(f"  Filename: {exe['filename']}")
        print(f"  Download: {exe['download_url']}")
        sha256 = exe.get('sha256', 'N/A')
        if sha256 and sha256 != 'N/A':
            print(f"  SHA256: {sha256[:32]}...")
        else:
            print(f"  SHA256: {sha256}")
        print(f"  Date: {exe.get('release_date', 'N/A')}")
        print(f"  Size: {exe.get('file_size', 'N/A')}")
else:
    print("\n❌ FAILED - No .exe files found")

# Test 3: Update checking
print("\n" + "=" * 70)
print("TEST 3: Update Checking")
print("=" * 70)

from datetime import datetime

# Simulate old version
old_sha256 = "old_hash_12345"
old_date = datetime(2025, 11, 1)

print(f"Local version:")
print(f"  SHA256: {old_sha256}")
print(f"  Date: {old_date}")

needs_update, update_info = parser2.check_for_updates_network(old_sha256, old_date)

if needs_update and update_info:
    print(f"\n✅ UPDATE AVAILABLE!")
    print(f"  New file: {update_info['filename']}")
    sha256 = update_info.get('sha256', 'N/A')
    if sha256 and sha256 != 'N/A':
        print(f"  SHA256: {sha256[:32]}...")
    else:
        print(f"  SHA256: {sha256}")
    print(f"  Date: {update_info.get('release_date', 'N/A')}")
else:
    print("\n✅ No update needed (or check failed)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

tests_passed = 0
if result1:
    tests_passed += 1
if result2:
    tests_passed += 1
if needs_update:
    tests_passed += 1

print(f"\nTests Passed: {tests_passed}/3")

if tests_passed == 3:
    print("\n🎉 ALL TESTS PASSED!")
    print("\nThe auto-updater is working correctly with:")
    print("  ✅ GitHub Release mode")
    print("  ✅ GitHub Network (Assets) mode")
    print("  ✅ Update detection")
    print("\nNo API required - uses expanded_assets endpoint!")
else:
    print(f"\n⚠️  {3 - tests_passed} test(s) failed")
    print("Check the output above for details")

print("\n" + "=" * 70)
