import cv2
import numpy as np
from moviepy import Clip


def transform_zoom(clip: Clip, zoom_speed=0.04):
    """
    Smooth, center-based zoom using cv2.warpAffine so there’s no pixel-jitter.
    zoom_speed is the factor per second (so at t seconds, scale = 1 + zoom_speed * t).
    """

    def cv2_smooth_zoom(get_frame, t):
        img = get_frame(t)  # frame is a H×W×C uint8 array
        h, w = img.shape[:2]

        # compute scale factor at time t
        scale = 1.0 + zoom_speed * t

        # build an affine matrix that scales about the image center
        center = (w * 0.5, h * 0.5)
        M = cv2.getRotationMatrix2D(center, angle=0.0, scale=scale)

        # warpAffine does: dst(x,y) = src(M_inv(x,y)), so we get a zoom about center
        # choose Lanczos for best quality
        zoomed = cv2.warpAffine(
            img,
            M,
            (w, h),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_REFLECT,  # reflect so you don’t get black borders
        )
        return zoomed

    # apply to the video frames (you can add apply_to="mask" if you have a mask)
    return clip.transform(cv2_smooth_zoom)
