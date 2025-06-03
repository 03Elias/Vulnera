

import os
from pathlib import Path
import zipfile


EXTENSION_LANGUAGE_MAP = {
    "py": "Python",
    "js": "JavaScript",
    "java": "Java",
    "c": "C",
    "cpp": "C++",
    "cc": "C++",
    "cxx": "C++",
    "cs": "C#",
    "go": "Go",
    "rs": "Rust",
    "ts": "TypeScript",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "ex": "Elixir",
    "exs": "Elixir",
    "json": "JSON",
    "node": "Node"
}

def get_language_from_extension(ext: str) -> str:
    return EXTENSION_LANGUAGE_MAP.get(ext.lower(), "")


def process_file(file_path: Path, base_path: Path):
    """
    Process a single file to extract filename, folder, language, and code.
    """
    ext = file_path.suffix.lstrip('.')
    language = get_language_from_extension(ext)
    if not language:
        return []

    try:
        code_text = file_path.read_text(encoding='utf-8')
    except Exception:
        return []

    try:
        rel_path = file_path.relative_to(base_path)
    except ValueError:
        rel_path = file_path.name

    
    rel_folder = rel_path.parent
    folder_str = rel_folder.as_posix() if rel_folder.parts else ''

    return [{
        "filename": rel_path.as_posix(),
        "folder": folder_str,
        "language": language,
        "code": code_text
    }]


def scan_path(input_path: Path):
    """
    Scan a directory on disk recursively.
    """
    results = []
    if input_path.is_file():
        results.extend(process_file(input_path, input_path.parent))
    else:
        for root, _, files in os.walk(input_path):
            for fname in files:
                file_path = Path(root) / fname
                results.extend(process_file(file_path, input_path))
    return results


def scan_upload(file_path: Path, temp_dir: Path):
    """
    Handle an uploaded file. If it's a zip, extract and scan directory.
    Otherwise treat as a single source file.

    Returns a list of scan results with folder info.
    """
    if zipfile.is_zipfile(file_path):
        extract_dir = temp_dir / (file_path.stem + "_unzipped")
        with zipfile.ZipFile(file_path, 'r') as z:
            z.extractall(extract_dir)
        return scan_path(extract_dir)
    else:
        return process_file(file_path, temp_dir)
