import json
from typing import List, Dict, Any

def generate_script_from_text(text: str, chapter_id: str) -> List[Dict[str, Any]]:
    """
    Generates a simple script from raw text by splitting it into paragraphs.

    For the MVP, each paragraph is treated as a scene with a single narrator.

    Args:
        text: The full text of the chapter.
        chapter_id: A unique identifier for the chapter (e.g., 'chapter_01').

    Returns:
        A list of dictionaries, where each dictionary represents a scene.
        Example:
        [
            {
                "scene_id": "chapter_01_s001",
                "speaker": "narrador",
                "text": "This is the first paragraph."
            },
            ...
        ]
    """
    print("Generando guion a partir del texto...")

    # Split text into paragraphs (scenes) by splitting on double newlines
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    scenes = []
    for i, paragraph in enumerate(paragraphs):
        scene_id = f"{chapter_id}_s{i+1:03d}"
        scene_data = {
            "scene_id": scene_id,
            "speaker": "narrador",
            "text": paragraph
        }
        scenes.append(scene_data)

    print(f"Guion generado con {len(scenes)} escenas.")
    return scenes

def save_script_to_json(script: List[Dict[str, Any]], output_path: str):
    """
    Saves the generated script to a JSON file.

    Args:
        script: The list of scene dictionaries.
        output_path: The path to save the JSON file.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=4)
    print(f"Guion guardado en {output_path}")
