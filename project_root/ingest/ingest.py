import os

def ingest_text_file(filepath: str) -> str:
    """
    Reads the content of a text file.

    Args:
        filepath: The path to the text file.

    Returns:
        The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo no fue encontrado en la ruta: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Texto ingerido con éxito desde {filepath}")
    return content
