from gtts import gTTS
import os
from typing import List

def generate_audio_clips(paragraphs: List[str], output_dir: str, lang: str = 'es'):
    """
    Generates an audio clip for each paragraph and saves it to the output directory.
    Returns a list of paths to the generated clips.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_paths = []
    print(f"  - Generating {len(paragraphs)} clips in '{lang}'...")
    for i, p in enumerate(paragraphs):
        # A simple check to avoid trying to process empty strings
        if not p:
            continue
        try:
            tts = gTTS(p, lang=lang, slow=False)
            filepath = os.path.join(output_dir, f"clip_{i:03d}.mp3")
            tts.save(filepath)
            output_paths.append(filepath)
        except Exception as e:
            print(f"    - Error generating audio for paragraph {i}: {e}")
    return output_paths
