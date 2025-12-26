from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.services.camera_service import camera_service
import asyncio
from loguru import logger

router = APIRouter()

@router.websocket("/ws/stream")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established for video stream")
    
    # Ensure camera is started
    if not camera_service.is_running:
        camera_service.start()
    
    try:
        while True:
            frame_bytes = await camera_service.get_jpeg_frame()
            if frame_bytes:
                await websocket.send_bytes(frame_bytes)
            await asyncio.sleep(0.033)
    except WebSocketDisconnect:
        logger.info("WebSocket stream disconnected")
    except Exception as e:
        logger.error(f"WebSocket stream error: {e}")


@router.websocket("/ws/notifications")
async def notifications_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("New live notifications connection")
    
    queue = asyncio.Queue()
    
    async def subscriber(alert_data: dict):
        await queue.put(alert_data)

    from app.core.services.alert_manager import alert_manager
    alert_manager.subscribe(subscriber)
    
    try:
        while True:
            alert = await queue.get()
            await websocket.send_json(alert)
    except WebSocketDisconnect:
        logger.info("Notifications connection closed")
    except Exception as e:
        logger.error(f"Notifications error: {e}")
    finally:
        alert_manager.unsubscribe(subscriber)
