import streamlit as st
import os
import json

def run_review_ui():
    """
    A simple Streamlit UI to review the generated content for a chapter.
    """
    st.set_page_config(layout="wide", page_title="Revisión de Radioteatro")

    st.title("Herramienta de Revisión de Contenido Generado")
    st.markdown("Esta UI permite escuchar y revisar los resultados del pipeline de generación.")

    # --- Chapter Selection (for future use) ---
    # For now, we hardcode the chapter we've just processed.
    # A future improvement would be to list all directories in 'output/'.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(project_root, "output")
    chapter_id = "chapter_01"
    chapter_path = os.path.join(output_dir, chapter_id)

    st.header(f"Revisando Capítulo: `{chapter_id}`")

    if not os.path.exists(chapter_path):
        st.error(f"El directorio de salida para el capítulo '{chapter_id}' no fue encontrado. Asegúrate de que el pipeline se haya ejecutado correctamente.")
        return

    # --- Display Final Video ---
    st.subheader("Video Final Ensamblado")
    final_video_path = os.path.join(chapter_path, f"{chapter_id}_final.mp4")
    if os.path.exists(final_video_path):
        video_file = open(final_video_path, 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
    else:
        st.warning("No se encontró el archivo de video final.")

    # --- Display Scene-by-Scene Breakdown ---
    st.subheader("Revisión por Escena")
    scenes_json_path = os.path.join(chapter_path, "scenes.json")
    if not os.path.exists(scenes_json_path):
        st.error("No se encontró el archivo `scenes.json`. No se pueden mostrar las escenas.")
        return

    with open(scenes_json_path, 'r', encoding='utf-8') as f:
        scenes = json.load(f)

    for scene in scenes:
        scene_id = scene.get("scene_id", "N/A")
        with st.expander(f"**Escena:** `{scene_id}` - **Hablante:** `{scene.get('speaker', 'N/A')}`"):

            # Display text
            st.markdown("**Texto:**")
            st.write(scene.get("text", "*Sin texto.*"))

            # Display audio
            st.markdown("**Audio Generado:**")
            audio_path = scene.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                audio_file = open(audio_path, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/wav')
                st.info(f"Duración: {scene.get('duration', 0)} segundos")
            else:
                st.warning("No se encontró el archivo de audio para esta escena.")

            # Display image (placeholder for now)
            st.markdown("**Imagen Generada:**")
            image_path = scene.get("image_path")
            if image_path and os.path.exists(image_path):
                # We use the placeholder for all scenes in the MVP
                st.image(image_path, caption="Imagen de marcador de posición.", width=256)
            else:
                st.warning("No se encontró la imagen para esta escena.")

if __name__ == '__main__':
    run_review_ui()
