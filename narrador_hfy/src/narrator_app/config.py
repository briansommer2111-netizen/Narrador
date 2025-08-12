import yaml
from pydantic import BaseModel, Field
from typing import Dict, Any

class Config:
    """Carga y valida la configuración desde un archivo YAML."""
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def get_config(self) -> Dict[str, Any]:
        # En una app más compleja, aquí se usaría Pydantic para validar la estructura
        return self.config
