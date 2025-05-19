# Effect registry
from moviepy.Clip import Clip
from moviepy import vfx

from src.custom_effects.zoom import transform_zoom

EFFECT_REGISTRY = {}


def register_effect(name):
    def decorator(fn):
        EFFECT_REGISTRY[name] = fn
        return fn

    return decorator


# Example custom_effects


@register_effect("fadein")
def fadein(clip: Clip, value: float):
    return clip.with_effects([vfx.FadeIn(value)])


@register_effect("fadeout")
def fadeout(clip: Clip, value: float):
    return clip.with_effects([vfx.FadeOut(value)])


@register_effect("zoom")
def zoom(clip: Clip, value: float):
    return transform_zoom(clip, value)


@register_effect("rotate")
def rotate(clip: Clip, value: float):
    return clip.with_effects([vfx.Rotate(value)])


@register_effect("slidein")
def slidein(clip: Clip, value: float):
    return clip.with_effects([vfx.SlideIn(duration=value, side="left")])
