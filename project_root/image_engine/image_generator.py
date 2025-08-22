import os
from typing import List, Dict, Any
from PIL import Image

def generate_images_for_script(
    script: List[Dict[str, Any]],
    assets_dir: str,
    chapter_id: str
) -> List[Dict[str, Any]]:
    """
    Generates placeholder images for each scene in the script.

    This function creates a valid, black PNG image file to be used as a
    placeholder if one does not already exist.

    Args:
        script: The list of scene dictionaries.
        assets_dir: The directory where assets are stored.
        chapter_id: The ID of the chapter.

    Returns:
        The updated script with 'image_path' added to each scene.
    """
    print("Asignando imágenes de marcador de posición a cada escena...")

    placeholder_image_name = "placeholder.png"
    placeholder_image_path = os.path.join(assets_dir, "images", placeholder_image_name)

    # Create a valid placeholder image using Pillow if it doesn't exist
    if not os.path.exists(placeholder_image_path):
        print(f"Creando imagen de marcador de posición válida en: {placeholder_image_path}")
        os.makedirs(os.path.dirname(placeholder_image_path), exist_ok=True)
        # Create a 1024x1024 black image
        img = Image.new('RGB', (1024, 1024), color = 'black')
        img.save(placeholder_image_path, 'PNG')

    for scene in script:
        scene['image_path'] = placeholder_image_path

    print("Imágenes de marcador de posición asignadas.")
    return script
