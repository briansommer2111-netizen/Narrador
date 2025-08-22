import os

def read_text_file(filepath: str) -> str:
    """Reads a text file and returns its content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return content
