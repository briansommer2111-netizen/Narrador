import logging
import os
import torch
from TTS.api import TTS
from pydub import AudioSegment
from typing import Dict, List

from ..data_structures import Story, Dialogue, Character
from ..utils import TTSError

logger = logging.getLogger(__name__)

class TTSIntegration:
    """
    Gestiona la síntesis de voz usando Coqui TTS (XTTSv2).
    Convierte un guion estructurado en archivos de audio.
    """

    def __init__(self, config: Dict):
        self.config = config.get('tts', {})
        self.paths_config = config.get('paths', {})
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Inicializando TTSIntegration en el dispositivo: {self.device}")

        self._load_model()
        self._load_voice_bank()

    def _load_model(self):
        try:
            model_name = self.config.get('model', 'tts_models/multilingual/multi-dataset/xtts_v2')
            logger.info(f"Cargando modelo TTS: {model_name}...")
            self.tts_engine = TTS(model_name).to(self.device)
            logger.info("Modelo TTS cargado correctamente.")
        except Exception as e:
            logger.error(f"No se pudo cargar el modelo TTS. Asegúrate de que los modelos están descargados. Error: {e}")
            raise TTSError("Fallo al inicializar el modelo TTS.") from e

    def _load_voice_bank(self):
        self.voice_bank: Dict[str, str] = {}
        voice_bank_path = self.paths_config.get('voice_bank', 'data/voice_bank')
        logger.info(f"Cargando banco de voces desde: {voice_bank_path}")
        
        if not os.path.isdir(voice_bank_path):
            logger.warning(f"El directorio del banco de voces no existe: {voice_bank_path}")
            return

        for filename in os.listdir(voice_bank_path):
            if filename.endswith(".wav"):
                archetype = os.path.splitext(filename)[0]
                self.voice_bank[archetype] = os.path.join(voice_bank_path, filename)
        
        logger.info(f"Voces cargadas: {list(self.voice_bank.keys())}")

    def synthesize_script(self, story: Story, temp_audio_dir: str) -> Story:
        logger.info(f"Iniciando síntesis de voz para la historia: '{story.title}'")
        os.makedirs(temp_audio_dir, exist_ok=True)
        
        char_map = {char.id: char for char in story.characters}
        char_map['narrator'] = Character(id='narrator', name='Narrador', voice_archetype=self.config.get('narrator_voice', 'narrador'))

        for i, dialogue in enumerate(story.script):
            output_path = os.path.join(temp_audio_dir, f"segment_{i:04d}.wav")
            
            character = char_map.get(dialogue.character_id)
            if not character:
                logger.warning(f"Personaje con ID '{dialogue.character_id}' no encontrado. Usando voz de narrador.")
                character = char_map['narrator']

            voice_archetype = character.voice_archetype
            speaker_wav_path = self.voice_bank.get(voice_archetype)

            if not speaker_wav_path:
                logger.error(f"Arquetipo de voz '{voice_archetype}' no encontrado en el banco de voces. Usando voz de narrador por defecto.")
                speaker_wav_path = self.voice_bank.get(char_map['narrator'].voice_archetype)
                if not speaker_wav_path:
                     raise TTSError("No se encuentra ni la voz del personaje ni la del narrador.")

            try:
                logger.debug(f"Generando audio para: [{character.name}] '{dialogue.text[:30]}...'")
                self.tts_engine.tts_to_file(
                    text=dialogue.text,
                    speaker_wav=speaker_wav_path,
                    language=self.config.get('language', 'es'),
                    file_path=output_path,
                )
                dialogue.audio_path = output_path
            except Exception as e:
                logger.error(f"Fallo al generar audio para el segmento {i}: {e}")
                dialogue.audio_path = None
        
        logger.info("Síntesis de voz completada para todos los segmentos.")
        return story
