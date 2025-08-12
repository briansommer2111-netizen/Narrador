import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict
from urllib.parse import urlparse

# Asumimos que estas importaciones vienen de nuestros otros módulos
from ..data_structures import Story
from ..utils import StoryProcessingError, NetworkError

# Configurar un logger específico para este módulo
logger = logging.getLogger(__name__)

class StoryProcessor:
    """
    Clase para adquirir, parsear y limpiar historias desde URLs de Reddit.
    """

    def __init__(self, config: Dict):
        """
        Inicializa el procesador con la configuración de la aplicación.

        Args:
            config (Dict): Un diccionario de configuración.
        """
        self.config = config
        self.session = requests.Session()
        # Es buena práctica usar un User-Agent para no ser bloqueado
        self.session.headers.update({
            "User-Agent": "NarratorApp/1.0 (compatible; +http://localhost)"
        })
        logger.info("StoryProcessor inicializado.")

    def get_story_from_url(self, url: str) -> Story:
        """
        Método principal que orquesta la obtención y procesamiento de una historia.

        Args:
            url (str): La URL de la publicación de Reddit.

        Returns:
            Story: Un objeto Story con los datos procesados.

        Raises:
            ValueError: Si la URL no es válida.
            NetworkError: Si hay problemas de conexión.
            StoryProcessingError: Si no se puede parsear la historia.
        """
        if not self._is_valid_reddit_url(url):
            raise ValueError(f"La URL proporcionada no es una URL de Reddit válida: {url}")

        html = self._fetch_html(url)
        story = self._parse_story(html, url)
        
        return story

    def _fetch_html(self, url: str) -> str:
        """Obtiene el contenido HTML de una URL."""
        try:
            logger.info(f"Obteniendo historia desde: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al intentar obtener la URL {url}: {e}")
            raise NetworkError(f"No se pudo conectar a {url}.") from e

    def _parse_story(self, html: str, url: str) -> Story:
        """Parsea el HTML para extraer metadatos y el contenido principal de la historia."""
        logger.info("Parseando el contenido HTML de la historia.")
        try:
            soup = BeautifulSoup(html, 'html.parser')

            title_element = soup.find('h1')
            title = title_element.get_text(strip=True) if title_element else "Título no encontrado"

            author_element = soup.find('a', href=lambda href: href and '/user/' in href)
            author = author_element.get_text(strip=True) if author_element else "Autor desconocido"
            
            post_content_div = soup.find('div', {'data-click-id': 'text'})
            
            if not post_content_div:
                 logger.error("No se encontró el div principal del contenido. La estructura de Reddit puede haber cambiado.")
                 raise StoryProcessingError("No se pudo encontrar el contenedor principal del post.")

            paragraphs = [p.get_text(strip=True) for p in post_content_div.find_all('p')]
            
            main_text = "\n\n".join(paragraphs)

            if not main_text:
                logger.warning("El texto principal de la historia está vacío.")

            story_data = {
                "url": url,
                "title": title,
                "author": author,
                "original_text": main_text,
            }
            
            logger.info(f"Historia '{title}' parseada correctamente.")
            return Story(**story_data)

        except Exception as e:
            logger.error(f"Error al parsear el HTML: {e}")
            raise StoryProcessingError("El formato del HTML no es el esperado.") from e

    def _is_valid_reddit_url(self, url: str) -> bool:
        """Valida si una URL pertenece a un post de reddit.com."""
        parsed_url = urlparse(url)
        return parsed_url.hostname in ('www.reddit.com', 'reddit.com') and '/r/HFY/comments/' in parsed_url.path
