import io
from typing import Any, Optional

import requests
from loguru import logger
from pydantic import ValidationError

from ..adapters.database import DatabaseInterface
from ..core.config import OLX_BASE_URL, OLX_REQUEST_TIMEOUT, SEARCH_PARAMS
from ..core.models import Offer
from ..services.image_service import ImageProcessor, MemoryImageProcessor
from ..services.telegram_service import TelegramService


class OLXScrapingService:

    def __init__(
        self,
        database: DatabaseInterface,
        telegram_service: TelegramService,
        image_processor: ImageProcessor | MemoryImageProcessor,
    ) -> None:
        self.database = database
        self.telegram_service = telegram_service
        self.image_processor = image_processor
        self.session = requests.Session()
        logger.info("OLX scraping service initialized")

    def fetch_and_process_offers(self) -> None:
        try:
            offers_data = self._fetch_offers_from_api()
            if not offers_data:
                logger.warning("No offers data received from API")
                return

            new_offers = self._filter_new_offers(offers_data)
            logger.info("Found %d new offers to process" % len(new_offers))

            for offer in new_offers:
                self._process_single_offer(offer)

        except Exception as e:
            logger.exception("Error in fetch_and_process_offers: %s" % e)

    def _fetch_offers_from_api(self) -> list[dict[str, Any]]:
        try:
            response = self.session.get(
                OLX_BASE_URL, params=SEARCH_PARAMS, timeout=OLX_REQUEST_TIMEOUT
            )
            response.raise_for_status()

            json_data = response.json()

            if not json_data.get("data"):
                logger.warning("API response contains no data")
                return []

            # Reverse order to process oldest first
            offers_data: list[dict[str, Any]] = json_data["data"][::-1]
            logger.debug("Fetched %s offers from API" % len(offers_data))
            return offers_data

        except requests.RequestException as e:
            logger.error("API request failed: %s" % e)
            return []
        except ValueError as e:
            logger.error("Invalid JSON response: %s" % e)
            return []

    def _filter_new_offers(self, offers_data: list[dict[str, Any]]) -> list[Offer]:
        new_offers: list[Offer] = []

        for offer_data in offers_data:
            try:
                offer = Offer(**offer_data)

                if offer.id and not self.database.check_offer_exists(offer.id):
                    new_offers.append(offer)

            except ValidationError as e:
                logger.warning("Invalid offer data: %s" % e)
                continue

        return new_offers

    def _process_single_offer(self, offer: Offer) -> None:
        if not offer.id:
            logger.warning("Offer missing ID, skipping")
            return

        try:
            # Add to database first to prevent reprocessing
            self.database.add_offer_id(offer.id)

            # Create photo collage if photos available
            photo = self._create_offer_collage(offer)

            # Send message to Telegram
            success = self.telegram_service.send_offer_message(offer, photo)

            if success:
                logger.info("Successfully processed: %s" % offer.url)
            else:
                logger.warning("Failed to send message for offer %s" % offer.id)

        except Exception as e:
            logger.exception("Error processing offer %s: %s" % (offer.id, e))

    def _create_offer_collage(self, offer: Offer) -> Optional[str | bytes]:
        if not offer.photos:
            logger.debug("No photos available for offer %s" % offer.id)
            return None

        # Extract photo URLs
        photo_urls = []
        for photo in offer.photos:
            if photo.link:
                primary_url = photo.link.split(";")[0]
                photo_urls.append(primary_url)

        if not photo_urls:
            logger.debug("No valid photo URLs for offer %s" % offer.id)
            return None

        # Handle single photo vs collage
        if len(photo_urls) == 1:
            return photo_urls[0]  # Return URL directly for single photo

        # Create collage for multiple photos
        if offer.id is not None:
            return self.image_processor.create_photo_collage(photo_urls, offer.id)
        else:
            logger.warning("Offer missing ID, cannot create collage")
            return None

    def close(self) -> None:
        self.session.close()
        logger.info("OLX scraping service closed")
