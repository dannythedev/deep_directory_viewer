import hashlib
import math
import os
from datetime import datetime

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
    ext_dictionary = {
        "Video": [
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.3gp',
            '.ts', '.vob', '.ogv', '.rm', '.swf', '.m4v', '.f4v', '.f4p', '.f4a', '.f4b'
        ],
        "Image": [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp', '.heif', '.raw',
            '.cr2', '.nef', '.orf', '.sr2', '.dng', '.indd', '.eps', '.ai', '.psd', '.svg', '.pdf'
        ],
        "Audio": [
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.opus',
            '.midi', '.ra', '.au', '.cda', '.ape', '.wma', '.mka', '.mod', '.s3m', '.it', '.xm'
        ],
        "Document": [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
            '.rtf', '.txt', '.csv', '.html', '.xml', '.json', '.epub', '.mobi', '.djvu', '.tex',
            '.md', '.log', '.yaml', '.conf', '.ini'
        ],
        "Archive": [
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.z', '.lzh', '.cab',
            '.arj', '.ace', '.uue', '.bin', '.dump', '.dmg', '.pkg', '.tar.gz', '.tar.bz2'
        ],
        "Executable": [
            '.exe', '.bat', '.cmd', '.app', '.sh', '.msi', '.pkg', '.jar', '.run', '.bin',
            '.out', '.appimage', '.apk', '.dmg', '.deb', '.rpm', '.wsf'
        ],
        "Script": [
            '.py', '.js', '.rb', '.pl', '.php', '.cgi', '.asp', '.jsp', '.html', '.css',
            '.sh', '.bash', '.vbs', '.ps1', '.command', '.sublime-build', '.sublime-project'
        ],
        "Font": [
            '.ttf', '.otf', '.woff', '.woff2', '.eot', '.pfb', '.afm', '.fnt', '.fon', '.type1'
        ],
        "Database": [
            '.db', '.sql', '.sqlite', '.mdb', '.accdb', '.dbf', '.sqlitedb', '.sqlite3', '.frm',
            '.myd', '.myi', '.ibd', '.ibdata1'
        ],
        "Config": [
            '.conf', '.ini', '.yaml', '.yml', '.json', '.xml', '.properties', '.cfg', '.config'
        ],
        "Web": [
            '.html', '.htm', '.xhtml', '.php', '.asp', '.jsp', '.css', '.js', '.json', '.xml', '.rss'
        ],
        "Email": [
            '.eml', '.msg', '.mbox', '.pst', '.ost', '.emlx'
        ],
        "CAD": [
            '.dwg', '.dxf', '.stl', '.iges', '.step', '.3dm', '.skp'
        ],
        "Virtualization": [
            '.vmdk', '.vdi', '.vhd', '.qcow2', '.ovf', '.ova', '.iso'
        ],
        "Log": [
            '.log', '.out', '.trace', '.debug'
        ],
        "Folder":
        ['']
    }

    for key in ext_dictionary:
        if ext in ext_dictionary[key]:
            return key
    return "Unknown"