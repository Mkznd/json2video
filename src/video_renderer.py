import tempfile
import requests
from moviepy import *
from src.effects import EFFECT_REGISTRY
from src.models import VideoRequest, TextOverlay, TransitionType, Transition
from src.utils import download_file


def compose_with_transition(clips, transition: Transition):
    # 1) keep first clip as‐is
    final_clips = []

    # 2) apply transition to each subsequent clip
    for i, clip in enumerate(clips):
        match transition.type:
            case TransitionType.CROSSFADE:
                clip = clip.with_effects([vfx.CrossFadeIn(transition.duration)])
            case TransitionType.SLIDE:
                clip = clip.with_effects(
                    [vfx.SlideIn(duration=transition.duration, side="top")]
                )
            case _:
                raise ValueError(f"Unknown transition type: {transition.type}")
        final_clips.append(clip)

    # 3) concatenate so that each clip overlaps the previous by `duration` seconds
    return concatenate_videoclips(
        final_clips, method="compose", padding=-transition.duration
    )


def add_text_overlays(base_clip, overlays: list[TextOverlay]):
    txt_clips = []
    for item in overlays:
        txt_clips.append(item.compile(base_clip))

    return CompositeVideoClip([base_clip] + txt_clips).with_duration(base_clip.duration)


def create_video(config: VideoRequest, output_path: str):
    clips = [item.compile() for item in config.timeline]
    base_clip = compose_with_transition(clips, config.transition)

    if config.text_overlays:
        base_clip = add_text_overlays(base_clip, config.text_overlays)

    if config.audio:
        audio_path = download_file(config.audio)
        audio = (
            AudioFileClip(audio_path)
            .with_effects([afx.AudioLoop(duration=base_clip.duration * 2)])
            .subclipped(end_time=base_clip.duration)
        )
        base_clip = base_clip.with_audio(audio)

    base_clip.write_videofile(output_path, fps=24)
