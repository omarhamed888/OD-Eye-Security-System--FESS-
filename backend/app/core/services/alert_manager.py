from typing import List, Callable, Tuple
import asyncio
from loguru import logger

class AlertManager:
    def __init__(self):
        # Store (callback, loop) tuples
        self.subscribers: List[Tuple[Callable, asyncio.AbstractEventLoop]] = []

    def subscribe(self, callback: Callable):
        try:
            loop = asyncio.get_event_loop()
            self.subscribers.append((callback, loop))
            logger.debug(f"New subscriber added to AlertManager. Total: {len(self.subscribers)}")
        except RuntimeError:
            logger.error("Failed to subscribe: No event loop in current thread")

    def unsubscribe(self, callback: Callable):
        self.subscribers = [s for s in self.subscribers if s[0] != callback]
        logger.debug(f"Subscriber removed. Total: {len(self.subscribers)}")

    async def broadcast(self, alert_data: dict):
        """Broadcast alert to all subscribers, handling different event loops."""
        if not self.subscribers:
            logger.debug("No subscribers to broadcast to")
            return
        
        logger.info(f"Broadcasting alert: {alert_data.get('title')}")
        
        for callback, loop in self.subscribers:
            if loop.is_running():
                # Use run_coroutine_threadsafe to bridge threads/loops safely
                asyncio.run_coroutine_threadsafe(callback(alert_data), loop)
            else:
                logger.warning("Subscriber loop is not running")

# Global instance
alert_manager = AlertManager()
