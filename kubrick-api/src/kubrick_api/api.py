import shutil
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from uuid import uuid4

import click
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastmcp.client import Client
from loguru import logger

from kubrick_api.agent import GroqAgent
from kubrick_api.config import get_settings
from kubrick_api.models import (
    AssistantMessageResponse,
    GenerateMTBHighlightRequest,
    GenerateMTBHighlightResponse,
    ProcessVideoRequest,
    ProcessVideoResponse,
    ResetMemoryResponse,
    UserMessageRequest,
    VideoUploadResponse,
)

settings = get_settings()


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = GroqAgent(
        name="kubrick",
        mcp_server=settings.MCP_SERVER,
        disable_tools=["process_video"],
    )
    app.state.bg_task_states = dict()
    yield
    app.state.agent.reset_memory()


app = FastAPI(
    title="Kubrick API",
    description="An AI-powered sports assistant API using OpenAI",
    docs_url="/docs",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media serving
app.mount("/media", StaticFiles(directory="shared_media"), name="media")


@app.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation
    """
    return {"message": "Welcome to Kubrick API. Visit /docs for documentation"}


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)
    return {"task_id": task_id, "status": status}


@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, bg_tasks: BackgroundTasks, fastapi_request: Request):
    """
    Process a video and return the results
    """
    task_id = str(uuid4())
    bg_task_states = fastapi_request.app.state.bg_task_states

    async def background_process_video(video_path: str, task_id: str):
        """
        Background task to process the video
        """
        bg_task_states[task_id] = TaskStatus.IN_PROGRESS

        if not Path(video_path).exists():
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=404, detail="Video file not found")

        try:
            mcp_client = Client(settings.MCP_SERVER)
            async with mcp_client:
                _ = await mcp_client.call_tool("process_video", {"video_path": request.video_path})
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=500, detail=str(e))
        bg_task_states[task_id] = TaskStatus.COMPLETED

    bg_tasks.add_task(background_process_video, request.video_path, task_id)
    return ProcessVideoResponse(message="Task enqueued for processing", task_id=task_id)


@app.post("/chat", response_model=AssistantMessageResponse)
async def chat(request: UserMessageRequest, fastapi_request: Request):
    """
    Chat with the AI assistant

    Args:
        request: ChatRequest containing the message and optional image URL

    Returns:
        ChatResponse containing the assistant's response
    """
    agent = fastapi_request.app.state.agent
    await agent.setup()

    try:
        response = await agent.chat(request.message, request.video_path, request.image_base64)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset-memory")
async def reset_memory(fastapi_request: Request):
    """
    Reset the memory of the agent
    """
    agent = fastapi_request.app.state.agent
    agent.reset_memory()
    return ResetMemoryResponse(message="Memory reset successfully")


@app.post("/upload-video", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video and return the path
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        shared_media_dir = Path("shared_media")
        shared_media_dir.mkdir(exist_ok=True)

        video_path = Path(shared_media_dir / file.filename)
        if not video_path.exists():
            with open(video_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        return VideoUploadResponse(message="Video uploaded successfully", video_path=str(video_path))
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-mtb-highlight")
async def generate_mtb_highlight(
    request: GenerateMTBHighlightRequest,
    bg_tasks: BackgroundTasks,
    fastapi_request: Request
):
    """
    Generate MTB action highlight reel from a processed video.

    This endpoint uses the generate_mtb_highlight_reel MCP tool to:
    1. Detect action highlights in the video
    2. Assemble them into a final highlight reel

    Args:
        request: Contains video_path, target_duration_seconds, min_action_score, use_ffmpeg

    Returns:
        task_id for background processing or direct output_path if synchronous
    """
    task_id = str(uuid4())
    bg_task_states = fastapi_request.app.state.bg_task_states

    async def background_generate_highlight(
        video_path: str,
        target_duration: float,
        min_score: float,
        use_ffmpeg: bool,
        task_id: str
    ):
        """Background task to generate MTB highlight reel."""
        bg_task_states[task_id] = {
            "status": TaskStatus.IN_PROGRESS,
            "message": "Analyzing video for action moments..."
        }

        try:
            # Call MCP tool via client
            client = Client(settings.MCP_SERVER)

            logger.info(f"Generating MTB highlight: {video_path}, target={target_duration}s, score={min_score}")

            result = await client.call_tool(
                "generate_mtb_highlight_reel",
                video_path=video_path,
                target_duration_seconds=target_duration,
                min_action_score=min_score,
                use_ffmpeg=use_ffmpeg
            )

            if result.get("error"):
                bg_task_states[task_id] = {
                    "status": TaskStatus.FAILED,
                    "message": result["error"]
                }
            else:
                bg_task_states[task_id] = {
                    "status": TaskStatus.COMPLETED,
                    "message": "Highlight reel generated successfully!",
                    "output_path": result.get("output_path"),
                    "num_highlights": result.get("num_highlights", 0),
                    "total_duration": result.get("total_duration", 0)
                }
                logger.info(f"MTB highlight generated: {result.get('output_path')}")

        except Exception as e:
            logger.error(f"Error generating MTB highlight: {e}")
            bg_task_states[task_id] = {
                "status": TaskStatus.FAILED,
                "message": str(e)
            }

    # Start background task
    bg_tasks.add_task(
        background_generate_highlight,
        request.video_path,
        request.target_duration_seconds,
        request.min_action_score or 60.0,
        request.use_ffmpeg,
        task_id
    )

    bg_task_states[task_id] = {
        "status": TaskStatus.PENDING,
        "message": "Starting highlight generation..."
    }

    return GenerateMTBHighlightResponse(
        message="MTB highlight generation started",
        task_id=task_id
    )


@app.get("/media/{file_path:path}")
async def serve_media(file_path: str):
    """
    Serve media files from the shared_media directory
    """
    try:
        clean_path = Path(file_path).name
        media_file = Path("shared_media") / clean_path

        if not media_file.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(str(media_file))
    except Exception as e:
        logger.error(f"Error serving media file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/media/{file_path:path}")
async def delete_media(file_path: str):
    """
    Delete a video or highlight file from shared_media directory.

    Supports deleting:
    - Original videos: /media/video.mp4
    - Highlights: /media/highlights/video_highlights_....mp4
    """
    try:
        # Support both formats: with or without "shared_media/" prefix
        if file_path.startswith("shared_media/"):
            relative_path = file_path.replace("shared_media/", "")
        else:
            relative_path = file_path

        media_file = Path("shared_media") / relative_path

        if not media_file.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Security check: ensure file is within shared_media directory
        if not str(media_file.resolve()).startswith(str(Path("shared_media").resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        media_file.unlink()
        logger.info(f"Deleted file: {media_file}")

        return {"message": "File deleted successfully", "file_path": file_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/highlights")
async def list_highlights():
    """
    List all saved highlight videos with metadata.

    Returns list of highlights with:
    - filename: Name of the highlight file
    - path: Relative path (for API calls)
    - size: File size in bytes
    - created: Creation timestamp
    - original_video: Name of the source video (parsed from filename)
    """
    try:
        highlights_dir = Path("shared_media/highlights")
        highlights_dir.mkdir(parents=True, exist_ok=True)

        highlights = []

        for file in sorted(highlights_dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True):
            # Parse filename: {original}_highlights_{timestamp}_{uuid}.mp4
            filename = file.name
            original_video = filename.split("_highlights_")[0] if "_highlights_" in filename else "unknown"

            highlights.append({
                "filename": filename,
                "path": f"highlights/{filename}",
                "size": file.stat().st_size,
                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                "created": file.stat().st_mtime,
                "original_video": original_video
            })

        return {
            "highlights": highlights,
            "count": len(highlights),
            "total_size_mb": round(sum(h["size"] for h in highlights) / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Error listing highlights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/storage-info")
async def get_storage_info():
    """
    Get storage information about shared_media directory.

    Returns:
    - total_files: Number of files
    - total_size_mb: Total size in MB
    - videos_count: Number of original videos
    - videos_size_mb: Size of original videos
    - highlights_count: Number of highlights
    - highlights_size_mb: Size of highlights
    """
    try:
        shared_media = Path("shared_media")
        highlights_dir = shared_media / "highlights"

        # Count videos (root level, excluding highlights folder)
        videos = [f for f in shared_media.glob("*.mp4") if f.is_file()]
        videos_size = sum(f.stat().st_size for f in videos)

        # Count highlights
        highlights_dir.mkdir(parents=True, exist_ok=True)
        highlights = list(highlights_dir.glob("*.mp4"))
        highlights_size = sum(f.stat().st_size for f in highlights)

        total_size = videos_size + highlights_size

        return {
            "total_files": len(videos) + len(highlights),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "videos": {
                "count": len(videos),
                "size_mb": round(videos_size / (1024 * 1024), 2)
            },
            "highlights": {
                "count": len(highlights),
                "size_mb": round(highlights_size / (1024 * 1024), 2)
            }
        }
    except Exception as e:
        logger.error(f"Error getting storage info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@click.command()
@click.option("--port", default=8080, help="FastAPI server port")
@click.option("--host", default="0.0.0.0", help="FastAPI server host")
def run_api(port, host):
    import uvicorn

    uvicorn.run("api:app", host=host, port=port, loop="asyncio")


if __name__ == "__main__":
    run_api()
