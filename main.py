import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from settings import settings
from src.models import VideoRequest, VideoResponse
from src.video_renderer import create_video
from google.cloud import storage
import tempfile

app = FastAPI()


@app.post("/render")
def render_video(payload: VideoRequest):
    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    output_path = tmp_file.name
    filename = f"{uuid.uuid4().hex}.mp4"
    try:
        create_video(payload, output_path)
        storage_client = storage.Client()
        bucket = storage_client.bucket(settings.bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(output_path)
        return VideoResponse(url=blob.public_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass  # You can schedule cleanup later
