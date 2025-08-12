import logging
import re
import spacy
from typing import Dict, List, Set

from ..data_structures import Story, Dialogue, Character
from ..utils import AnalysisError

logger = logging.getLogger(__name__)

class DialogueAnalyzer:
    """
    Analiza una historia para identificar personajes, extraer diálogos,
    y anotar información relevante como emociones o acciones.
    """

    def __init__(self, config: Dict):
        self.config = config.get('dialogue_analysis', {})
        self.model_name = self.config.get('spacy_model', 'es_core_news_md')
        
        try:
            logger.info(f"Cargando modelo de spaCy: {self.model_name}...")
            self.nlp = spacy.load(self.model_name)
            logger.info("Modelo de spaCy cargado correctamente.")
        except OSError:
            logger.error(f"Modelo de spaCy '{self.model_name}' no encontrado.")
            logger.info(f"Por favor, descárgalo ejecutando: python -m spacy download {self.model_name}")
            raise AnalysisError(f"Modelo de spaCy no encontrado: {self.model_name}")

        self.dialogue_pattern = re.compile(r'["«“]([^"»”]+)["»”]')
        self.speech_verbs = {'dijo', 'preguntó', 'respondió', 'gritó', 'susurró', 'exclamó'}

    def analyze_story(self, story: Story) -> Story:
        if not story.translated_text:
            logger.warning("El texto traducido está vacío. No se puede analizar.")
            return story

        logger.info(f"Iniciando análisis de diálogos para: '{story.title}'")
        
        doc = self.nlp(story.translated_text)
        
        characters = self._identify_characters(doc)
        story.characters = characters
        logger.info(f"Personajes identificados: {[c.name for c in characters]}")

        script = self._create_script(doc, characters)
        story.script = script
        logger.info(f"Guion creado con {len(script)} entradas.")

        return story

    def _identify_characters(self, doc) -> List[Character]:
        char_names = set()
        for ent in doc.ents:
            if ent.label_ == "PER":
                char_names.add(ent.text)
        
        characters = [
            Character(id=name.lower().replace(" ", "_"), name=name, voice_archetype="default")
            for name in char_names
        ]
        return characters

    def _create_script(self, doc, characters: List[Character]) -> List[Dialogue]:
        script: List[Dialogue] = []
        char_map = {c.name: c.id for c in characters}
        last_speaker_id = "narrator"

        paragraphs = doc.text.split('\n\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            matches = list(self.dialogue_pattern.finditer(paragraph))
            
            if not matches:
                script.append(Dialogue(text=paragraph, character_id="narrator"))
                last_speaker_id = "narrator"
            else:
                last_match_end = 0
                for match in matches:
                    start, end = match.span()
                    
                    narrator_text = paragraph[last_match_end:start].strip()
                    if narrator_text:
                        script.append(Dialogue(text=narrator_text, character_id="narrator"))

                    dialogue_text = match.group(1).strip()
                    
                    context_text = paragraph[end:].strip()
                    speaker_id = self._find_speaker_in_context(context_text, char_map)

                    if speaker_id:
                        last_speaker_id = speaker_id
                    
                    script.append(Dialogue(text=dialogue_text, character_id=last_speaker_id))
                    last_match_end = end
                
                final_narrator_text = paragraph[last_match_end:].strip()
                if final_narrator_text:
                    script.append(Dialogue(text=final_narrator_text, character_id="narrator"))

        return script

    def _find_speaker_in_context(self, context: str, char_map: Dict[str, str]) -> str | None:
        context_doc = self.nlp(context)
        for token in context_doc:
            if token.lemma_ in self.speech_verbs:
                for child in token.children:
                    if child.dep_ == "nsubj":
                        if child.text in char_map:
                            return char_map[child.text]
        
        for name, char_id in char_map.items():
            if name in context:
                return char_id
        
        return None
