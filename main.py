from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from src.models import VideoRequest
from src.video_renderer import create_video
import tempfile

app = FastAPI()


@app.post("/render")
def render_video(payload: VideoRequest):
    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    output_path = tmp_file.name

    try:
        create_video(payload, output_path)
        return FileResponse(
            path=output_path, filename="video.mp4", media_type="video/mp4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass  # You can schedule cleanup later
