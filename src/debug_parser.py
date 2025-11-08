"""
Debug script to test GitHub page parsing
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://github.com/SuurStofi/auto-updater-app/releases/tag/auto-updating-app"

# Convert to expanded_assets endpoint
expanded_url = url.replace('/releases/tag/', '/releases/expanded_assets/')

print("=" * 70)
print(f"Testing URL: {url}")
print(f"Expanded Assets URL: {expanded_url}")
print("=" * 70)

try:
    # Test expanded_assets endpoint
    print("\n" + "=" * 70)
    print("Testing EXPANDED_ASSETS endpoint (loads assets immediately)")
    print("=" * 70)
    
    response = requests.get(expanded_url)
    response.raise_for_status()
    print(f"✓ Successfully fetched page (Status: {response.status_code})")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links
    print("\n" + "=" * 70)
    print("Searching for .exe links...")
    print("=" * 70)
    
    all_links = soup.find_all('a', href=True)
    exe_links = [link for link in all_links if '.exe' in link.get('href', '').lower()]
    
    print(f"\nTotal links on page: {len(all_links)}")
    print(f"Links containing '.exe': {len(exe_links)}")
    
    if exe_links:
        print("\n.exe Links found:")
        for i, link in enumerate(exe_links, 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"\n{i}. Text: {text}")
            print(f"   Href: {href}")
            print(f"   Full URL: https://github.com{href}" if not href.startswith('http') else f"   Full URL: {href}")
    
    # Search for clipboard-copy elements
    print("\n" + "=" * 70)
    print("Searching for SHA256 hashes...")
    print("=" * 70)
    
    clipboard_elements = soup.find_all('clipboard-copy')
    sha256_elements = [elem for elem in clipboard_elements if 'sha256' in elem.get('value', '').lower()]
    
    print(f"\nTotal clipboard-copy elements: {len(clipboard_elements)}")
    print(f"Elements with SHA256: {len(sha256_elements)}")
    
    if sha256_elements:
        print("\nSHA256 hashes found:")
        for i, elem in enumerate(sha256_elements, 1):
            value = elem.get('value', '')
            aria_label = elem.get('aria-label', '')
            print(f"\n{i}. Value: {value}")
            print(f"   Label: {aria_label}")
    
    # Search for relative-time elements
    print("\n" + "=" * 70)
    print("Searching for dates...")
    print("=" * 70)
    
    time_elements = soup.find_all('relative-time')
    print(f"\nTotal relative-time elements: {len(time_elements)}")
    
    if time_elements:
        print("\nDates found:")
        for i, elem in enumerate(time_elements[:5], 1):  # Show first 5
            datetime = elem.get('datetime', '')
            text = elem.get_text(strip=True)
            print(f"\n{i}. DateTime: {datetime}")
            print(f"   Display: {text}")
    
    # Look for asset information
    print("\n" + "=" * 70)
    print("Searching for asset containers...")
    print("=" * 70)
    
    # Try different container patterns
    patterns = [
        ('Box-row', soup.find_all('div', class_=re.compile(r'Box-row'))),
        ('d-flex containers', soup.find_all('div', class_=re.compile(r'd-flex'))),
        ('data-view-component', soup.find_all('div', {'data-view-component': 'true'})),
    ]
    
    for pattern_name, elements in patterns:
        print(f"\n{pattern_name}: {len(elements)} found")
    
    # Save HTML for manual inspection
    with open('github_page_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("\n✓ Saved HTML to 'github_page_debug.html' for manual inspection")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Debug complete!")
print("=" * 70)
