import streamlit as st
import os
import sys
import yaml

# Añadir el directorio src al path para poder importar nuestros módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Importar todos los módulos de la aplicación
from narrator_app.config import Config
from narrator_app.modules.story_processor import StoryProcessor
from narrator_app.modules.translator import StoryTranslator
from narrator_app.modules.dialogue_analyzer import DialogueAnalyzer
from narrator_app.modules.tts_integration import TTSIntegration
from narrator_app.modules.video_creator import VideoCreator
from narrator_app.utils import setup_logging

# --- Configuración de la Página y Logging ---
st.set_page_config(layout="wide", page_title="Narrador de Historias HFY")
setup_logging()

# --- Carga de Configuración ---
@st.cache_resource
def load_app_config():
    """Carga la configuración principal de la aplicación."""
    config_loader = Config('config.yaml')
    return config_loader.get_config()

config = load_app_config()

# --- Inicialización de Módulos (en caché para rendimiento) ---
@st.cache_resource
def get_story_processor():
    return StoryProcessor(config)

@st.cache_resource
def get_translator():
    return StoryTranslator(config)

@st.cache_resource
def get_dialogue_analyzer():
    return DialogueAnalyzer(config)

@st.cache_resource
def get_tts_integration():
    return TTSIntegration(config)

@st.cache_resource
def get_video_creator():
    return VideoCreator(config)

# --- Lógica de la Interfaz de Usuario (Asistente por Pasos) ---

st.title("🤖 Asistente de Creación de Videos de Narración HFY")
st.markdown("Sigue los pasos para convertir una historia de Reddit en un video narrado.")

if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.story = None
    st.session_state.final_video_path = None

# --- PASO 1: INGRESAR URL ---
if st.session_state.step == 1:
    st.header("Paso 1: Obtener la Historia")
    url = st.text_input("Pega la URL de una historia de r/HFY:", "https://www.reddit.com/r/HFY/comments/3h9bz3/oc_the_last_angel/")
    
    if st.button("1. Procesar Historia"):
        with st.spinner("Obteniendo y limpiando la historia..."):
            try:
                processor = get_story_processor()
                st.session_state.story = processor.get_story_from_url(url)
                st.session_state.step = 2
                st.rerun()
            except Exception as e:
                st.error(f"Error al procesar la historia: {e}")

# --- PASO 2: TRADUCIR ---
if st.session_state.step == 2:
    st.header("Paso 2: Traducir la Historia")
    st.subheader("Texto Original")
    st.text_area("Original", st.session_state.story.original_text, height=200)
    
    if st.button("2. Traducir a Español"):
        with st.spinner("Traduciendo... (esto puede tardar varios minutos)"):
            try:
                translator = get_translator()
                st.session_state.story = translator.translate_story(st.session_state.story)
                st.session_state.step = 3
                st.rerun()
            except Exception as e:
                st.error(f"Error durante la traducción: {e}")

# --- PASO 3: ANALIZAR DIÁLOGOS ---
if st.session_state.step == 3:
    st.header("Paso 3: Analizar Diálogos y Asignar Voces")
    st.subheader("Texto Traducido")
    st.text_area("Traducido", st.session_state.story.translated_text, height=200)

    if st.button("3. Analizar Personajes y Diálogos"):
        with st.spinner("Analizando estructura del diálogo..."):
            try:
                analyzer = get_dialogue_analyzer()
                st.session_state.story = analyzer.analyze_story(st.session_state.story)
                st.session_state.step = 4
                st.rerun()
            except Exception as e:
                st.error(f"Error durante el análisis de diálogos: {e}")

# --- PASO 4: ASIGNAR VOCES ---
if st.session_state.step == 4:
    st.header("Paso 4: Asignar Voces a Personajes")
    
    voice_bank_path = config.get('paths', {}).get('voice_bank', 'data/voice_bank')
    if not os.path.exists(voice_bank_path) or not os.listdir(voice_bank_path):
        st.warning(f"No se encontraron voces en la carpeta '{voice_bank_path}'. Por favor, añade archivos .wav para continuar.")
    else:
        available_voices = [f.split('.')[0] for f in os.listdir(voice_bank_path) if f.endswith('.wav')]
        st.info(f"Voces disponibles: {', '.join(available_voices)}")

        for i, char in enumerate(st.session_state.story.characters):
            selected_voice = st.selectbox(
                f"Voz para {char.name}:",
                options=available_voices,
                key=f"char_voice_{i}"
            )
            char.voice_archetype = selected_voice

        if st.button("4. Generar Audio con Voces Asignadas"):
            with st.spinner("Generando audio... Este es el paso más largo."):
                try:
                    tts = get_tts_integration()
                    temp_audio_dir = "data/temp_audio"
                    st.session_state.story = tts.synthesize_script(st.session_state.story, temp_audio_dir)
                    st.session_state.step = 5
                    st.rerun()
                except Exception as e:
                    st.error(f"Error durante la síntesis de voz: {e}")

# --- PASO 5: CREAR VIDEO ---
if st.session_state.step == 5:
    st.header("Paso 5: Crear el Video Final")
    st.success("¡El audio ha sido generado! Listo para crear el video.")
    
    with st.expander("Ver guion final y audios generados"):
        for dialogue in st.session_state.story.script:
            st.markdown(f"**[{dialogue.character_id.upper()}]**: {dialogue.text}")
            if dialogue.audio_path and os.path.exists(dialogue.audio_path):
                st.audio(dialogue.audio_path)

    if st.button("5. Crear Video"):
        with st.spinner("Creando el video..."):
            try:
                video_creator = get_video_creator()
                output_path = f"data/output/{st.session_state.story.title.replace(' ', '_')}.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                video_creator.create_video_from_story(st.session_state.story, output_path)
                st.session_state.final_video_path = output_path
                st.session_state.step = 6
                st.rerun()
            except Exception as e:
                st.error(f"Error durante la creación del video: {e}")

# --- PASO 6: FINALIZADO ---
if st.session_state.step == 6:
    st.header("¡Proceso Completado!")
    st.balloons()
    st.success(f"Tu video ha sido creado con éxito.")
    
    video_path = st.session_state.final_video_path
    with open(video_path, "rb") as file:
        st.download_button(
            label="Descargar Video",
            data=file,
            file_name=os.path.basename(video_path),
            mime="video/mp4"
        )
    
    st.video(video_path)

    if st.button("Crear otro video"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
