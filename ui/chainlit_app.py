import asyncio
import os
import shutil
from enum import Enum

import aiohttp
import chainlit as cl


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


API_BASE_URL = "http://agent-api:8080"  # Adjust to your FastAPI server address
DEFAULT_RETRY_INTERVAL_SEC = 10
os.makedirs("videos", exist_ok=True)


@cl.on_chat_start
async def start():
    files = None

    while not files:
        files = await cl.AskFileMessage(
            content="Please upload your video to begin!",
            accept=[".mp4"],
            max_size_mb=100,
        ).send()

    video_file = files[0]
    dest_path = os.path.join("videos", video_file.name)
    shutil.move(video_file.path, dest_path)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/process-video",
                json={"video_path": dest_path},
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    await cl.Message(content=f"Error from API: {error_text}").send()
                    return

                data = await response.json()
                task_id = data.get("task_id")
                await cl.Message(content="Your video is being processed, please wait...").send()

                while True:
                    await asyncio.sleep(DEFAULT_RETRY_INTERVAL_SEC)  # wait before polling
                    async with session.get(f"{API_BASE_URL}/task-status/{task_id}") as status_resp:
                        if status_resp.status != 200:
                            await cl.Message(content="Error checking task status").send()
                            break
                        status_data = await status_resp.json()
                        status = status_data.get("status")

                        if TaskStatus(status) == TaskStatus.COMPLETED:
                            elements = [
                                cl.Video(name=video_file.name, path=dest_path, display="inline"),
                            ]
                            await cl.Message(
                                content="Video processed successfully!",
                                elements=elements,
                            ).send()
                            break
                        elif TaskStatus(status) == TaskStatus.FAILED:
                            await cl.Message(content="Video processing failed.").send()
                            break

            cl.user_session.set("video_path", dest_path)

        except Exception as e:
            await cl.Message(content=f"Error handling video file: {str(e)}").send()


@cl.on_message
async def main(message: cl.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/chat",
                json={"message": message.content, "video_path": cl.user_session.get("video_path")},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    await cl.Message(content=data["response"]).send()
                else:
                    error_text = await response.text()
                    await cl.Message(content=f"Error from API: {error_text}").send()
    except Exception as e:
        await cl.Message(content=f"Error communicating with API: {str(e)}").send()
