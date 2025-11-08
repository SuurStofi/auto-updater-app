import hashlib
from pathlib import Path

def calculate_sha256(file_path):
    """
    Calculate SHA256 hash of a file
    
    Args:
        file_path: Path to the file (string or Path object)
    
    Returns:
        str: Hexadecimal SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def verify_file_hash(file_path, expected_hash):
    """
    Verify file's SHA256 hash matches expected value
    
    Args:
        file_path: Path to the file
        expected_hash: Expected SHA256 hash (can include 'sha256:' prefix)
    
    Returns:
        bool: True if hashes match, False otherwise
    """
    # Remove 'sha256:' prefix if present
    if expected_hash.startswith('sha256:'):
        expected_hash = expected_hash.replace('sha256:', '')
    
    calculated_hash = calculate_sha256(file_path)
    
    return calculated_hash.lower() == expected_hash.lower()

def get_file_metadata(file_path):
    """
    Get file metadata including hash and modification time
    
    Args:
        file_path: Path to the file
    
    Returns:
        dict: Contains 'sha256', 'modified_date', and 'size'
    """
    from datetime import datetime
    
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    sha256 = calculate_sha256(path)
    modified_time = datetime.fromtimestamp(path.stat().st_mtime)
    
    return {
        'sha256': sha256,
        'modified_date': modified_time.isoformat(),
        'size': path.stat().st_size
    }
