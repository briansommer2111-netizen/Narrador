import logging
import sys

# --- Excepciones Personalizadas ---
class AppError(Exception):
    """Clase base para excepciones de la aplicación."""
    pass

class StoryProcessingError(AppError):
    """Error durante el procesamiento o scraping de la historia."""
    pass

class NetworkError(AppError):
    """Error relacionado con la red."""
    pass

class TranslationError(AppError):
    """Error durante la traducción."""
    pass

class AnalysisError(AppError):
    """Error durante el análisis de diálogos."""
    pass

class TTSError(AppError):
    """Error en la síntesis de voz."""
    pass

class VideoError(AppError):
    """Error en la creación de video."""
    pass


# --- Sistema de Logging ---
def setup_logging(log_level=logging.INFO):
    """Configura el sistema de logging para la aplicación."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
