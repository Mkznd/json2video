from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional


class Effects(BaseModel):
    fadein: Optional[float] = None
    fadeout: Optional[float] = None
    zoom: Optional[float] = None
    rotate: Optional[float] = None
    slidein: Optional[int] = None


class ImageItem(BaseModel):
    url: HttpUrl
    duration: float
    effects: Optional[Effects] = None


class TextOverlay(BaseModel):
    text: str
    start: float
    end: float
    position: Optional[str] = "center"
    fontsize: Optional[int] = 32
    color: Optional[str] = "white"


class VideoRequest(BaseModel):
    images: List[ImageItem]
    audio: Optional[HttpUrl] = None
    text_overlays: List[TextOverlay] = Field(default_factory=list)
