from pydub import AudioSegment
import os
from typing import List

def assemble_audio(clip_paths: List[str], output_path: str):
    """
    Assembles a list of audio clips into a single audio file.
    This function will raise exceptions if pydub fails, for example,
    if ffmpeg is not found or a file is corrupt.
    """
    if not clip_paths:
        print("  - No audio clips to assemble.")
        return

    print(f"  - Assembling {len(clip_paths)} clips...")
    final_audio = AudioSegment.empty()
    for clip_path in clip_paths:
        # Let exceptions from pydub propagate up to the orchestrator
        segment = AudioSegment.from_file(clip_path)
        # Add a small silence between clips for better pacing
        final_audio += segment + AudioSegment.silent(duration=500) # 0.5 seconds of silence

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Export the final audio. Let exceptions propagate.
    final_audio.export(output_path, format="mp3")
    print(f"  - Final audio saved to {output_path}")
