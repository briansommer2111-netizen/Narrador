import os
from pydub import AudioSegment
from typing import List, Dict, Any
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip

def assemble_audio_from_script(script: List[Dict[str, Any]], output_path: str):
    """
    Assembles a single audio file by concatenating audio clips from a script.
    (This function is kept for audio-only pipeline runs).
    """
    print("Ensamblando el archivo de audio final...")

    final_audio = AudioSegment.empty()

    for scene in script:
        audio_path = scene.get('audio_path')
        if audio_path and os.path.exists(audio_path):
            try:
                scene_audio = AudioSegment.from_wav(audio_path)
                final_audio += scene_audio
                print(f" -> Añadiendo {os.path.basename(audio_path)} al montaje de audio.")
            except Exception as e:
                print(f"Error al procesar el archivo de audio {audio_path}: {e}")
        else:
            print(f"Advertencia: No se encontró el archivo de audio para la escena {scene.get('scene_id')}. Saltando.")

    try:
        final_audio.export(output_path, format="wav")
        print(f"Archivo de audio final guardado con éxito en: {output_path}")
    except Exception as e:
        print(f"Error al exportar el archivo de audio final: {e}")

def assemble_video_from_script(
    script: List[Dict[str, Any]],
    output_path: str,
    image_size: tuple = (1024, 1024)
):
    """
    Assembles a video from a script by combining images and audio.

    Args:
        script: The list of scene dictionaries with audio and image paths.
        output_path: The path to save the final MP4 video file.
        image_size: The desired output resolution (width, height).
    """
    print("Ensamblando el archivo de video final...")

    video_clips = []
    for scene in script:
        image_path = scene.get('image_path')
        audio_path = scene.get('audio_path')
        duration = scene.get('duration')

        if not all([image_path, audio_path, duration]):
            print(f"Advertencia: Faltan datos para la escena {scene.get('scene_id')}. Saltando.")
            continue

        if not os.path.exists(image_path) or not os.path.exists(audio_path):
            print(f"Advertencia: No se encontraron los archivos para la escena {scene.get('scene_id')}. Saltando.")
            continue

        try:
            # Create video clip from image
            video_clip = ImageClip(image_path, duration=duration).resize(width=image_size[0], height=image_size[1])

            # Create audio clip
            audio_clip = AudioFileClip(audio_path)

            # Set audio for the video clip
            video_clip = video_clip.set_audio(audio_clip)

            video_clips.append(video_clip)
            print(f" -> Clip de video creado para {scene.get('scene_id')}.")

        except Exception as e:
            # Moviepy can raise errors on malformed images, handle it gracefully.
            print(f"Error creando el clip para la escena {scene.get('scene_id')}: {e}")
            print("Se usará un clip negro como respaldo.")
            # Fallback to a black screen clip if image processing fails
            video_clip = ColorClip(size=image_size, color=(0, 0, 0), duration=duration)
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.set_audio(audio_clip)
            video_clips.append(video_clip)

    if not video_clips:
        print("Error: No se pudo crear ningún clip de video. Abortando ensamblaje.")
        return

    # Concatenate all clips into a single video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Write the final video to a file
    try:
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=24
        )
        print(f"Video final guardado con éxito en: {output_path}")
    except Exception as e:
        print(f"Error al escribir el archivo de video final: {e}")
