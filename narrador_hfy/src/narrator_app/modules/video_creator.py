import logging
import os
from moviepy.editor import (
    AudioFileClip, CompositeVideoClip, ImageClip, TextClip,
    concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont

from ..data_structures import Story, Dialogue
from ..utils import VideoError

logger = logging.getLogger(__name__)

class VideoCreator:
    """
    Crea un video final combinando audio, imágenes y subtítulos.
    """

    def __init__(self, config: dict):
        self.config = config.get('video', {})
        self.paths_config = config.get('paths', {})
        self.resolution = tuple(self.config.get('resolution', [1920, 1080]))
        self.fps = self.config.get('fps', 24)
        self.font = self.config.get('font', 'Arial')
        self.fontsize = self.config.get('fontsize', 48)
        self.font_color = self.config.get('font_color', 'white')
        logger.info("VideoCreator inicializado.")

    def create_video_from_story(self, story: Story, output_video_path: str):
        logger.info(f"Iniciando creación de video para: '{story.title}'")
        
        bg_image_path = self.config.get('default_background', 'data/default_bg.png')
        if not os.path.exists(bg_image_path):
            logger.warning(f"No se encontró la imagen de fondo. Creando una por defecto.")
            self._create_default_background(bg_image_path)

        video_segments = []

        title_clip = self._create_title_clip(story.title, story.author, bg_image_path)
        video_segments.append(title_clip)

        for dialogue in story.script:
            if not dialogue.audio_path or not os.path.exists(dialogue.audio_path):
                logger.warning(f"Saltando segmento sin audio: {dialogue.text[:30]}...")
                continue
            
            try:
                segment_clip = self._create_segment_clip(dialogue, bg_image_path)
                video_segments.append(segment_clip)
            except Exception as e:
                logger.error(f"No se pudo crear el clip para el segmento '{dialogue.text[:30]}...': {e}")

        if not video_segments:
            raise VideoError("No se pudo crear ningún segmento de video.")

        final_clip = concatenate_videoclips(video_segments, method="compose")

        try:
            logger.info(f"Exportando video final a: {output_video_path}")
            final_clip.write_videofile(
                output_video_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            logger.info("Video exportado con éxito.")
        except Exception as e:
            logger.error(f"Fallo al exportar el video final: {e}")
            raise VideoError("No se pudo escribir el archivo de video final.") from e

    def _create_title_clip(self, title: str, author: str, bg_path: str) -> CompositeVideoClip:
        duration = self.config.get('title_duration_s', 5)
        
        bg_clip = ImageClip(bg_path, duration=duration).resize(self.resolution)
        
        title_text = TextClip(
            txt=title,
            fontsize=self.fontsize * 1.5,
            color=self.font_color,
            font=self.font,
            size=self.resolution,
            method='caption'
        ).set_position(('center', 'center')).set_duration(duration)

        author_text = TextClip(
            txt=f"por {author}",
            fontsize=self.fontsize * 0.8,
            color=self.font_color,
            font=self.font
        ).set_position(('center', title_text.pos(title_text.start)[1] + title_text.size[1])).set_duration(duration)

        return CompositeVideoClip([bg_clip, title_text, author_text])

    def _create_segment_clip(self, dialogue: Dialogue, bg_path: str) -> CompositeVideoClip:
        audio_clip = AudioFileClip(dialogue.audio_path)
        duration = audio_clip.duration
        
        bg_clip = ImageClip(bg_path, duration=duration).resize(self.resolution)
        
        text_size = (self.resolution[0] * 0.8, None) 
        subtitle_clip = TextClip(
            txt=dialogue.text,
            fontsize=self.fontsize,
            color=self.font_color,
            font=self.font,
            size=text_size,
            method='caption'
        ).set_position(('center', 'bottom')).set_duration(duration)

        composite_clip = CompositeVideoClip([bg_clip, subtitle_clip])
        composite_clip.audio = audio_clip
        
        return composite_clip

    def _create_default_background(self, path: str):
        img = Image.new('RGB', self.resolution, color = 'black')
        img.save(path)
