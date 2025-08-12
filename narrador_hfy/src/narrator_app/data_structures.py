from pydantic import BaseModel, Field
from typing import List, Optional

class Dialogue(BaseModel):
    text: str
    character_id: str = "narrator"
    emotion: Optional[str] = None
    audio_path: Optional[str] = None

class Character(BaseModel):
    id: str = Field(..., description="Identificador único, ej: 'capitana_eva'")
    name: str = Field(..., description="Nombre en la historia, ej: 'Capitana Eva'")
    voice_archetype: str = Field(..., description="Arquetipo de voz del banco, ej: 'heroina'")

class Story(BaseModel):
    url: str
    title: str
    author: str
    original_text: str
    translated_text: str = ""
    characters: List[Character] = []
    script: List[Dialogue] = [] # Guion final con narrador y diálogos
