import tempfile
import requests
from moviepy import *
from src.effects import EFFECT_REGISTRY
from src.models import VideoRequest, TextOverlay
from src.utils import download_file


def add_text_overlays(base_clip, overlays: list[TextOverlay]):
    txt_clips = []
    for item in overlays:
        txt_clips.append(item.compile(base_clip))

    return CompositeVideoClip([base_clip] + txt_clips).with_duration(base_clip.duration)


def create_video(config: VideoRequest, output_path: str):
    clips = []

    for item in config.timeline:
        clips.append(item.compile())

    base_clip = concatenate_videoclips(clips, method="compose")

    if config.text_overlays:
        base_clip = add_text_overlays(base_clip, config.text_overlays)

    if config.audio:
        audio_path = download_file(config.audio)
        audio = AudioFileClip(audio_path).subclipped(end_time=base_clip.duration)
        base_clip = base_clip.with_audio(audio)

    base_clip.write_videofile(output_path, fps=24)
