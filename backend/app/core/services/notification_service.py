import asyncio
from telegram import Bot
from loguru import logger
from app.core.config import settings
import os


class NotificationService:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.CHAT_ID
        self.bot = None
        
        if self.token and self.chat_id:
            try:
                self.bot = Bot(token=self.token)
                logger.info("Telegram Bot notification service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram Bot: {e}")

    async def send_telegram_alert(self, message: str, image_path: str = None):
        if not self.bot or not self.chat_id:
            logger.warning("Telegram notification skipped: Bot or Chat ID not configured")
            return False

        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=message
                    )
            else:
                await self.bot.send_message(chat_id=self.chat_id, text=message)
            
            logger.info("Telegram alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False


# Global instance
notification_service = NotificationService()
