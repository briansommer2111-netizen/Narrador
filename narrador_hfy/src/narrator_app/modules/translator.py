import logging
import re
import torch
from transformers import pipeline, MarianMTModel, MarianTokenizer
from typing import Dict, List, Set

from ..data_structures import Story
from ..utils import TranslationError

logger = logging.getLogger(__name__)

class StoryTranslator:
    """
    Clase para traducir el texto de una historia de inglés a español
    usando un modelo local de Hugging Face.
    """

    def __init__(self, config: Dict):
        self.config = config.get('translation', {})
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Inicializando StoryTranslator en el dispositivo: {self.device}")

        self.model_name = self.config.get('model', 'Helsinki-NLP/opus-mt-en-es')
        self.cache: Dict[str, str] = {}
        self.protected_terms: Set[str] = set(self.config.get('protected_terms', []))

        try:
            self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
            self.model = MarianMTModel.from_pretrained(self.model_name).to(self.device)
            logger.info(f"Modelo de traducción '{self.model_name}' cargado correctamente.")
        except Exception as e:
            logger.error(f"No se pudo cargar el modelo de traducción: {e}")
            raise TranslationError("Fallo al inicializar el modelo de traducción.") from e

    def translate_story(self, story: Story) -> Story:
        if not story.original_text:
            logger.warning("El texto original está vacío, no hay nada que traducir.")
            story.translated_text = ""
            return story

        logger.info(f"Iniciando traducción para la historia: '{story.title}'")

        paragraphs = story.original_text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        try:
            translated_paragraphs = self._translate_batch(paragraphs)
            story.translated_text = "\n\n".join(translated_paragraphs)
            logger.info("La historia ha sido traducida con éxito.")
        except Exception as e:
            logger.error(f"Ocurrió un error durante el proceso de traducción por lotes: {e}")
            raise TranslationError("No se pudo traducir la historia completa.") from e
            
        return story

    def _translate_batch(self, batch: List[str]) -> List[str]:
        texts_to_translate = [text for text in batch if text not in self.cache]
        
        if texts_to_translate:
            logger.info(f"Traduciendo un lote de {len(texts_to_translate)} párrafos.")
            
            protected_batch, terms_map = self._protect_terms(texts_to_translate)

            inputs = self.tokenizer(protected_batch, return_tensors="pt", padding=True, truncation=True).to(self.device)
            translated_tokens = self.model.generate(**inputs)
            raw_translations = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)

            restored_translations = self._restore_terms(raw_translations, terms_map)
            
            for original, translated in zip(texts_to_translate, restored_translations):
                self.cache[original] = translated

        return [self.cache[text] for text in batch]

    def _protect_terms(self, texts: List[str]) -> (List[str], List[Dict[str, str]]):
        all_terms = self.protected_terms.union(self._find_proper_nouns(texts))
        protected_texts = []
        terms_map = []

        for text in texts:
            current_map = {}
            temp_text = text
            for i, term in enumerate(all_terms):
                placeholder = f"__TERM{i}__"
                if re.search(r'\b' + re.escape(term) + r'\b', temp_text, re.IGNORECASE):
                    temp_text = re.sub(r'\b' + re.escape(term) + r'\b', placeholder, temp_text, flags=re.IGNORECASE)
                    current_map[placeholder] = term
            protected_texts.append(temp_text)
            terms_map.append(current_map)
            
        return protected_texts, terms_map

    def _restore_terms(self, texts: List[str], terms_map: List[Dict[str, str]]) -> List[str]:
        restored_texts = []
        for i, text in enumerate(texts):
            temp_text = text
            current_map = terms_map[i]
            for placeholder, term in current_map.items():
                temp_text = temp_text.replace(placeholder, term)
            restored_texts.append(temp_text)
        return restored_texts

    def _find_proper_nouns(self, texts: List[str]) -> Set[str]:
        proper_nouns = set()
        for text in texts:
            found = re.findall(r'(?<=\. )\b[A-Z][a-z]+\b|(?<=, )\b[A-Z][a-z]+\b', text)
            for noun in found:
                proper_nouns.add(noun)
        return proper_nouns
