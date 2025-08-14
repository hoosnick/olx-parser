import os
from typing import Tuple

from ..adapters.database import SQLiteDatabase
from ..services.image_service import ImageProcessor
from ..services.olx_service import OLXScrapingService
from ..services.telegram_service import TelegramService


class ApplicationFactory:

    @staticmethod
    def create_services() -> Tuple[OLXScrapingService, SQLiteDatabase]:
        os.makedirs("logs", exist_ok=True)

        database = SQLiteDatabase()

        telegram_service = TelegramService()
        image_processor = ImageProcessor()

        olx_service = OLXScrapingService(
            database=database,
            telegram_service=telegram_service,
            image_processor=image_processor,
        )

        return olx_service, database
