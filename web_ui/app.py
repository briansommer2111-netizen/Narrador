import streamlit as st
import os
import sys

# Add project root to sys.path to allow imports from other modules
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

    from script_generator.generator import text_to_paragraphs
    from ingest.ingest import read_text_file
except ImportError as e:
    st.error(f"Error importing modules: {e}. Please ensure the app is run from the project root.")
    st.stop()

# --- UI Configuration ---
st.set_page_config(
    page_title="Radioteatro - Revisión de Contenido",
    layout="wide"
)

st.title("Herramienta de Revisión de Radioteatro 🎭")

# --- Data Loading ---
# For the MVP, we hardcode the chapter we are reviewing.
# In the future, this could be a dropdown menu.
CHAPTER_ID = "capitulo_1"

# Define paths relative to the project root
INPUT_TEXT_PATH = os.path.join(project_root, "input", f"{CHAPTER_ID}.txt")
AUDIO_CLIPS_DIR = os.path.join(project_root, "data", "audio")
FINAL_AUDIO_PATH = os.path.join(project_root, "output", f"{CHAPTER_ID}_narrado.mp3")

# Load content
try:
    chapter_text = read_text_file(INPUT_TEXT_PATH)
    scenes = text_to_paragraphs(chapter_text)
except FileNotFoundError:
    st.error(f"No se encontró el archivo de texto de entrada: {INPUT_TEXT_PATH}")
    st.info("Asegúrate de haber ejecutado el pipeline principal (`orchestrator/orchestrator.py`) al menos una vez.")
    st.stop()


# --- Main Display ---
st.header(f"Revisión de: {CHAPTER_ID}")

st.info(f"""
Se han encontrado **{len(scenes)}** escenas (párrafos) para este capítulo.
A continuación puedes revisar el texto y el audio de cada una.
""")

# Display each scene with its audio clip
for i, scene_text in enumerate(scenes):
    st.markdown("---")
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader(f"📝 Escena {i+1}")
        st.write(scene_text)

    with col2:
        st.subheader(f"🔊 Audio de la Escena {i+1}")
        audio_clip_path = os.path.join(AUDIO_CLIPS_DIR, f"clip_{i:03d}.mp3")

        if os.path.exists(audio_clip_path):
            try:
                with open(audio_clip_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                st.error(f"No se pudo cargar el archivo de audio: {audio_clip_path}. Error: {e}")
        else:
            st.warning(f"No se encontró el archivo de audio para esta escena: {audio_clip_path}")

# --- Download Final Product ---
st.markdown("---")
st.header("Producto Final")

if os.path.exists(FINAL_AUDIO_PATH):
    st.write("Aquí puedes escuchar y descargar el capítulo completo ya ensamblado.")
    try:
        with open(FINAL_AUDIO_PATH, "rb") as final_audio_file:
            final_audio_bytes = final_audio_file.read()

        st.audio(final_audio_bytes, format='audio/mp3')

        st.download_button(
            label="📥 Descargar Audio Completo (.mp3)",
            data=final_audio_bytes,
            file_name=f"{CHAPTER_ID}_completo.mp3",
            mime="audio/mp3"
        )
    except Exception as e:
        st.error(f"No se pudo cargar el archivo de audio final: {FINAL_AUDIO_PATH}. Error: {e}")
else:
    st.warning(f"No se encontró el archivo de audio final: {FINAL_AUDIO_PATH}")
    st.info("Ejecuta el pipeline principal para generarlo.")
