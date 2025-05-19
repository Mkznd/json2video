import tempfile
import requests
from moviepy import *
from src.effects import EFFECT_REGISTRY
from src.models import VideoRequest


def download_file(url):
    r = requests.get(url)
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(r.content)
    tmp.close()
    return tmp.name


def apply_effects(clip, effects):
    for effect_name, value in effects.dict().items():
        if value is not None and effect_name in EFFECT_REGISTRY:
            clip = EFFECT_REGISTRY[effect_name](clip, value)
    return clip


def add_text_overlays(base_clip, overlays):
    txt_clips = []
    for item in overlays:
        txt = TextClip(
            font="fonts/Impact.ttf",
            text=item.text,
            font_size=item.fontsize,
            color=item.color,
            text_align="center",
            method="caption",
            size=(base_clip.w, base_clip.h),
        )
        txt.with_start(item.start)
        txt.with_duration(item.end - item.start)

        txt_clips.append(txt)
    return CompositeVideoClip([base_clip] + txt_clips).with_duration(base_clip.duration)


def create_video(config: VideoRequest, output_path: str):
    clips = []

    for item in config.images:
        img_path = download_file(item.url)
        clip = ImageClip(img_path).with_duration(item.duration)
        if item.effects:
            clip = apply_effects(clip, item.effects)
        clips.append(clip)

    base_clip = concatenate_videoclips(clips, method="compose")

    if config.text_overlays:
        base_clip = add_text_overlays(base_clip, config.text_overlays)

    if config.audio:
        audio_path = download_file(config.audio)
        audio = AudioFileClip(audio_path).subclipped(end_time=base_clip.duration)
        base_clip = base_clip.with_audio(audio)

    base_clip.write_videofile(output_path, fps=24)
