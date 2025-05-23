import os
import shutil
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from moviepy import VideoFileClip, AudioFileClip
from starlette.background import BackgroundTask

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


TMP_DIR = "tmp_combiner"
os.makedirs(TMP_DIR, exist_ok=True)


@app.post("/combine")
async def combine_endpoint(
    video: UploadFile = File(..., description="Video file (.webm)"),
    audio: UploadFile = File(..., description="Audio file (.webm)"),
):
    # Generate unique filenames
    vid_id = uuid.uuid4().hex
    aud_id = uuid.uuid4().hex
    out_id = uuid.uuid4().hex
    video_path = os.path.join(TMP_DIR, f"video_{vid_id}.webm")
    audio_path = os.path.join(TMP_DIR, f"audio_{aud_id}.webm")
    output_path = os.path.join(TMP_DIR, f"combined_{out_id}.webm")

    try:
        # Save uploaded files to disk
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Load clips
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        # Combine and write output
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(
            output_path,
            codec="libvpx-vp9",
            audio_codec="libvorbis",
            temp_audiofile=os.path.join(TMP_DIR, f"temp_{out_id}.webm"),
            remove_temp=True,
            threads=4,
            logger=None,
        )

    except Exception as e:
        # Cleanup on error
        for p in (video_path, audio_path, output_path):
            try:
                os.remove(p)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=str(e))

    # Cleanup inputs
    try:
        os.remove(video_path)
        os.remove(audio_path)
    except OSError:
        pass

    # Return combined file and schedule deletion
    return FileResponse(
        path=output_path,
        media_type="video/webm",
        filename=os.path.basename(output_path),
        background=BackgroundTask(lambda: shutil.rmtree(TMP_DIR, ignore_errors=True)),
    )
