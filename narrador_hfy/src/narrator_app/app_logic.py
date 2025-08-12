import logging
from typing import Callable, Any

# Importaciones de nuestros módulos
from .config import Config
from .data_structures import Story
from .modules.story_processor import StoryProcessor
from .modules.translator import StoryTranslator
from .modules.dialogue_analyzer import DialogueAnalyzer
from .modules.tts_integration import TTSIntegration
from .modules.video_creator import VideoCreator

logger = logging.getLogger(__name__)

class AppOrchestrator:
    """Coordina todos los módulos para ejecutar el flujo de trabajo completo."""

    def __init__(self, config: dict):
        self.config = config
        self.story_processor = StoryProcessor(config)
        self.translator = StoryTranslator(config)
        self.dialogue_analyzer = DialogueAnalyzer(config)
        self.tts_integration = TTSIntegration(config)
        self.video_creator = VideoCreator(config)
        logger.info("AppOrchestrator inicializado con todos los módulos.")

    def run_full_pipeline(self, url: str, progress_callback: Callable[[float, str], Any]):
        """
        Ejecuta el pipeline completo desde la URL hasta el video final.
        """
        try:
            progress_callback(0.05, "Obteniendo historia...")
            story = self.story_processor.get_story_from_url(url)

            progress_callback(0.15, "Traduciendo texto...")
            story = self.translator.translate_story(story)

            progress_callback(0.40, "Analizando diálogos...")
            story = self.dialogue_analyzer.analyze_story(story)
            
            progress_callback(0.50, "Generando audio (puede tardar)...")
            temp_audio_dir = "data/temp_audio"
            story = self.tts_integration.synthesize_script(story, temp_audio_dir)

            progress_callback(0.85, "Creando video final...")
            output_path = f"data/output/{story.title.replace(' ', '_')}.mp4"
            self.video_creator.create_video_from_story(story, output_path)
            
            progress_callback(1.0, "¡Completado!")
            return output_path

        except Exception as e:
            logger.error(f"Ha ocurrido un error en el pipeline: {e}", exc_info=True)
            raise
