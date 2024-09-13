import hashlib
import json
import math
import os
from datetime import datetime

with open('types.json', 'r') as file:
    EXT_DICTIONARY = json.load(file)

def list_files_and_folders(directory, include_hash, include_subfolders):
    """List files and folders with options to include hash, subfolders, and dates."""
    table = []
    if not include_subfolders:
        # Only list current directory
        files = os.listdir(directory)
        for name in files:
            file_path = os.path.join(directory, name)
            file_type = get_file_type(file_path)
            if os.path.isdir(file_path):
                creation_date = "-"
                modified_date = "-"
                table.append([file_type, file_path, creation_date, modified_date, "-", "-"] if include_hash else [file_type, file_path, creation_date, modified_date, "-", ""])
            elif os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                size_str = convert_bytes(size)
                creation_date = format_date(os.path.getctime(file_path))
                modified_date = format_date(os.path.getmtime(file_path))
                file_hash = get_file_hash(file_path) if include_hash else "-"
                table.append([file_type, file_path, creation_date, modified_date, size_str, file_hash])
    else:
        # Recursively list files and folders
        for root, dirs, files in os.walk(directory):
            for name in dirs:
                dir_path = os.path.join(root, name)
                file_type = get_file_type(dir_path)
                creation_date = format_date(os.path.getctime(dir_path))
                modified_date = format_date(os.path.getmtime(dir_path))
                table.append([file_type, dir_path, creation_date, modified_date, "-", "-"] if include_hash else [file_type, dir_path, creation_date, modified_date, "-", ""])
            for name in files:
                file_path = os.path.join(root, name)
                file_type = get_file_type(file_path)
                size = os.path.getsize(file_path)
                size_str = convert_bytes(size)
                creation_date = format_date(os.path.getctime(file_path))
                modified_date = format_date(os.path.getmtime(file_path))
                file_hash = get_file_hash(file_path) if include_hash else "-"
                table.append([file_type, file_path, creation_date, modified_date, size_str, file_hash])
    return table

def get_file_hash(file_path):
    """Compute the SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def convert_bytes(size):
    """Convert bytes to a human-readable format (KB, MB, GB, TB)."""
    if size == 0:
        return "0 Bytes"
    size_name = ("Bytes", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%s %s" % (s, size_name[i])

def format_date(timestamp):
    """Format a timestamp into a readable date string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_file_type(file_path):
    """Determine the type of a file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()

    for key in EXT_DICTIONARY:
        if ext in EXT_DICTIONARY[key]:
            return key
    return "Unknown"