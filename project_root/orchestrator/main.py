import os
import yaml
import sys

# Add project root to the Python path to allow for absolute imports
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root_path)

from ingest.ingest import ingest_text_file
from script_generator.generator import generate_script_from_text, save_script_to_json
from image_engine.image_generator import generate_images_for_script
from voice_engine.tts import generate_audio_for_script
from media_assembler.assembler import assemble_video_from_script

def load_config(config_path='config.yaml'):
    """Loads the YAML configuration file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    """Main orchestration function to run the pipeline."""
    print("--- Iniciando el pipeline de Novela a Radioteatro (con video) ---")

    # --- 1. Cargar Configuración ---
    try:
        config = load_config(os.path.join(project_root_path, 'config.yaml'))
    except FileNotFoundError:
        print("Error: No se encontró el archivo config.yaml. Asegúrate de que exista en la raíz del proyecto.")
        return

    # --- 2. Definir Rutas para un capítulo específico ---
    chapter_id = 'chapter_01'
    input_file = os.path.join(project_root_path, config['paths']['input'], f'{chapter_id}.txt')

    # Directorio de salida para este capítulo específico
    chapter_output_dir = os.path.join(project_root_path, config['paths']['output'], chapter_id)
    os.makedirs(chapter_output_dir, exist_ok=True)

    # Rutas para los artefactos generados
    script_json_path = os.path.join(chapter_output_dir, 'scenes.json')
    audio_output_dir = os.path.join(chapter_output_dir, 'audio')
    # Nuevo path para el video final
    final_video_path = os.path.join(chapter_output_dir, f'{chapter_id}_final.mp4')

    # --- 3. Ejecutar el Pipeline ---
    try:
        # Paso 1: Ingesta
        print("\n[Paso 1/5] Ingiriendo texto...")
        raw_text = ingest_text_file(input_file)

        # Paso 2: Generación de Guion
        print("\n[Paso 2/5] Generando guion...")
        script = generate_script_from_text(raw_text, chapter_id)

        # Paso 3: Generación de Imágenes (Placeholder)
        print("\n[Paso 3/5] Generando imágenes...")
        assets_path = os.path.join(project_root_path, config['paths']['assets'])
        script_with_images = generate_images_for_script(script, assets_path, chapter_id)

        # Paso 4: Generación de Voz
        print("\n[Paso 4/5] Generando audio con el motor de voz...")
        script_with_audio = generate_audio_for_script(script_with_images, audio_output_dir, config['models']['tts'])
        # Guardamos el script actualizado con todas las rutas y duraciones
        save_script_to_json(script_with_audio, script_json_path)

        # Paso 5: Ensamblaje de Video
        print("\n[Paso 5/5] Ensamblando video final...")
        image_size_tuple = tuple(config['assembly']['image_size'])
        assemble_video_from_script(script_with_audio, final_video_path, image_size_tuple)

    except Exception as e:
        print(f"\n--- Ocurrió un error durante la ejecución del pipeline ---")
        print(f"Error: {e}")
        return

    print("\n--- Pipeline completado con éxito ---")
    print(f"El video final se encuentra en: {final_video_path}")

if __name__ == '__main__':
    main()
