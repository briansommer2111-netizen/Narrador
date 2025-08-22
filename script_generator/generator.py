from typing import List

def text_to_paragraphs(text: str) -> List[str]:
    """Splits a block of text into paragraphs based on newline characters."""
    if not text:
        return []
    # Split by one or more newlines, and filter out any empty strings resulting from the split.
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    return paragraphs
