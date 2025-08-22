import json
import os
from typing import TypedDict, List, Dict, Any, Optional

# --- Data Structures for Type Hinting ---

class VoiceProfile(TypedDict):
    model: str
    preset: str

class CharacterProfile(TypedDict):
    id: str
    name: str
    description: str
    images: List[str]
    voice_profile: VoiceProfile
    image_embedding: Optional[List[float]] # Placeholder for CLIP/Faiss embedding
    permanent_changes: List[str]
    temporary_overrides: List[Any]

# A type for the entire character database
CharacterDB = Dict[str, CharacterProfile]


# --- Database Interaction Functions ---

def load_character_db(db_path: str) -> CharacterDB:
    """
    Loads the character database from a JSON file.
    Returns an empty dictionary if the file doesn't exist.
    """
    if not os.path.exists(db_path):
        return {}
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading character database from {db_path}: {e}")
        return {}

def get_character_by_id(db: CharacterDB, character_id: str) -> Optional[CharacterProfile]:
    """
    Retrieves a character profile from the database by its ID.
    """
    return db.get(character_id)

def save_character_db(db_path: str, db: CharacterDB):
    """
    Saves the entire character database to a JSON file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving character database to {db_path}: {e}")

def add_or_update_character(db: CharacterDB, profile: CharacterProfile):
    """
    Adds a new character or updates an existing one in the database dictionary.
    """
    character_id = profile.get("id")
    if character_id:
        db[character_id] = profile
    else:
        print("Error: Character profile must have an 'id' to be added or updated.")
