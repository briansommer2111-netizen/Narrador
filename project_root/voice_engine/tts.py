import os
import torch
import soundfile as sf
from typing import List, Dict, Any
from TTS.api import TTS

def get_device():
    """Checks for CUDA device and returns it, otherwise defaults to CPU."""
    if torch.cuda.is_available():
        print("GPU detectada. Usando CUDA.")
        return "cuda"
    else:
        print("GPU no detectada. Usando CPU.")
        return "cpu"

def generate_audio_for_script(
    script: List[Dict[str, Any]],
    output_dir: str,
    model_name: str = "tts_models/es/css10/vits"
) -> List[Dict[str, Any]]:
    """
    Generates audio for each scene in the script using a TTS model.

    Args:
        script: A list of scene dictionaries.
        output_dir: The directory to save the generated audio files.
        model_name: The Coqui TTS model to use.

    Returns:
        The updated script with 'audio_path' and 'duration' added to each scene.
    """
    print(f"Cargando modelo TTS: {model_name}...")
    device = get_device()
    tts = TTS(model_name=model_name).to(device)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("Generando archivos de audio para cada escena...")
    for scene in script:
        scene_id = scene["scene_id"]
        text = scene["text"]

        output_path = os.path.join(output_dir, f"{scene_id}.wav")

        try:
            # Generate audio and save to file
            tts.tts_to_file(text=text, file_path=output_path)

            # Get audio duration
            with sf.SoundFile(output_path) as f:
                duration = len(f) / f.samplerate

            # Update the scene dictionary
            scene['audio_path'] = output_path
            scene['duration'] = round(duration, 2)

            print(f" -> Audio generado para {scene_id} ({duration:.2f}s)")

        except Exception as e:
            print(f"Error generando audio para {scene_id}: {e}")
            scene['audio_path'] = None
            scene['duration'] = 0

    print("Proceso de generación de audio completado.")
    return script
