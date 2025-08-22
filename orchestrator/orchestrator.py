import yaml
import os
import sys
import json # For pretty printing the profile

# Add project root to sys.path to allow imports from other modules
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

    from ingest.ingest import read_text_file
    from script_generator.generator import text_to_paragraphs
    from voice_engine.engine import generate_audio_clips
    from media_assembler.assembler import assemble_audio
    from memory_db.database import load_character_db, get_character_by_id
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you are running this script from the project's root directory or that the project root is in your PYTHONPATH.")
    sys.exit(1)


def load_config(config_path='config.yaml'):
    """Loads the YAML configuration file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    """Main orchestration function for the MVP."""
    print("--- Starting MVP Audio Pipeline ---")

    try:
        # Construct absolute path for config file
        config_path = os.path.join(project_root, 'config.yaml')
        print(f"Loading configuration from {config_path}...")
        config = load_config(config_path)

        # --- Define paths from config ---
        input_file = os.path.join(project_root, config['paths']['input_dir'], 'capitulo_1.txt')
        db_path = os.path.join(project_root, 'memory_db', 'characters.json')
        audio_clips_dir = os.path.join(project_root, config['data_paths']['audio_clips'])
        final_audio_path = os.path.join(project_root, config['paths']['output_dir'], 'capitulo_1_narrado.mp3')

        # 1. Ingest
        print(f"\n[Step 1/5] Ingesting text from: {input_file}")
        raw_text = read_text_file(input_file)
        print("  - Ingestion successful.")

        # 2. Character Memory Lookup (NEW STEP)
        print(f"\n[Step 2/5] Looking up characters in memory...")
        character_db = load_character_db(db_path)
        # In a real scenario, this would use NLP to find all character names.
        # For the MVP, we'll just search for a specific character we know is there.
        if "Isaac" in raw_text:
            print("  - Found mention of 'Isaac'.")
            isaac_profile = get_character_by_id(character_db, "isaac")
            if isaac_profile:
                print("  - Successfully retrieved profile for 'isaac':")
                # Pretty print the profile dictionary
                print(json.dumps(isaac_profile, indent=2, ensure_ascii=False))
            else:
                print("  - WARNING: 'Isaac' mentioned in text but not found in database.")
        else:
            print("  - No known characters found in this text segment.")

        # 3. Generate Script
        print("\n[Step 3/5] Generating script (splitting into paragraphs)...")
        paragraphs = text_to_paragraphs(raw_text)
        print(f"  - Found {len(paragraphs)} paragraphs.")

        # 4. Voice Engine
        print("\n[Step 4/5] Generating audio clips...")
        lang = config['voice_engine']['params']['lang']
        clip_paths = generate_audio_clips(paragraphs, audio_clips_dir, lang)
        print(f"  - Generated {len(clip_paths)} audio clips in '{audio_clips_dir}'")

        # 5. Media Assembler
        print("\n[Step 5/5] Assembling final audio file...")
        assemble_audio(clip_paths, final_audio_path)

        print("\n--- Pipeline Finished Successfully! ---")

    except FileNotFoundError as e:
        print(f"\n--- PIPELINE FAILED ---")
        print(f"Error: A required file was not found.")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n--- PIPELINE FAILED ---")
        print(f"An unexpected error occurred: {type(e).__name__}")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
