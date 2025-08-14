import os
from typing import Final

TELEGRAM_BOT_TOKEN: Final[str] = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN")
TELEGRAM_CHANNEL_ID: Final[int] = int(os.environ.get("TELEGRAM_CHANNEL_ID", "0"))

OLX_BASE_URL: Final[str] = "https://www.olx.uz/api/v1/offers"
OLX_REQUEST_TIMEOUT: Final[float] = 5.0

# Search Parameters
SEARCH_PARAMS: Final[dict[str, int | str]] = {
    "offset": 0,
    "limit": 50,
    "category_id": 1147,  # Real estate category
    "region_id": 5,  # Tashkent region
    "district_id": 26,  # Tashkent district
    "city_id": 5,  # Tashkent city
    "distance": 10,
    "currency": "UYE",
    "sort_by": "created_at:desc",
    "filter_float_price:from": 100,
    "filter_float_price:to": 350,
    "filter_float_number_of_rooms:from": 1,
    "filter_float_number_of_rooms:to": 6,
    "filter_refiners": "",
}

DATABASE_NAME: Final[str] = "offers.db"

LOGGING_LEVEL: Final[str] = "INFO"
LOG_TO_FILE: Final[bool] = False

COLLAGE_OUTPUT_WIDTH: Final[int] = 3840
COLLAGE_OUTPUT_HEIGHT: Final[int] = 2160
COLLAGE_BORDER_WIDTH: Final[float] = 0.006
MAX_DOWNLOAD_WORKERS: Final[int] = 5
MAX_ASPECT_RATIO: Final[float] = 1.5

SCHEDULER_INTERVAL_MINUTES: Final[int] = 1
MESSAGE_DELAY_SECONDS: Final[list[int]] = [1, 2, 3]
MAX_DESCRIPTION_LENGTH: Final[int] = 800

DOWNLOADS_DIR: Final[str] = "downloads"
TEMP_PHOTOS_PREFIX: Final[str] = "photos_"
PHOTO_COLLAGE_DIR: Final[str] = "photo_collages"
