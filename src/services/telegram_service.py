import io
import os
import random
import time
from contextlib import suppress
from datetime import datetime
from typing import Optional, Union

import telebot
from loguru import logger
from selectolax.lexbor import LexborHTMLParser
from telebot import types

from ..core.config import (
    MAX_DESCRIPTION_LENGTH,
    MESSAGE_DELAY_SECONDS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
)
from ..core.models import Offer


class TelegramService:

    def __init__(
        self,
        token: str = TELEGRAM_BOT_TOKEN,
        channel_id: int = TELEGRAM_CHANNEL_ID,
    ) -> None:
        self.bot = telebot.TeleBot(token, parse_mode="HTML", num_threads=5)
        self.channel_id = channel_id
        logger.info("Telegram service initialized")

    def send_offer_message(
        self,
        offer: Offer,
        photo_path: Optional[Union[bytes, str]] = None,
    ) -> bool:
        try:
            message_text = self._format_offer_message(offer)
            reply_markup = self._create_offer_keyboard(offer)

            if photo_path and not isinstance(photo_path, str):
                success = self._send_photo_message(
                    message_text, photo_path, reply_markup
                )
            elif isinstance(photo_path, str) and photo_path.startswith("https"):
                success = self._send_photo_message(
                    message_text, photo_path, reply_markup
                )
            else:
                success = self._send_text_message(message_text, reply_markup)

            if success:
                self._random_delay()

            return success

        except Exception as e:
            logger.exception(
                "Error sending Telegram message for offer %s: %s" % (offer.id, e)
            )
            return False
        finally:
            return True
            # Clean up local photo file
            if (
                photo_path
                and os.path.exists(photo_path)
                and not photo_path.startswith("https")
            ):
                with suppress(Exception):
                    os.unlink(photo_path)
                    logger.debug("Cleaned up photo file: %s" % photo_path)

    def _format_offer_message(self, offer: Offer) -> str:
        template = (
            "🏘 <b>{title}</b>\n\n"
            "<i>{description}</i>\n\n"
            "📍 <a href='{location_url}'>{location_name}</a>\n"
            "💵 <b>{price}</b> | <b>{published_time}</b>"
        )

        # Extract price information
        price = self._extract_price(offer)

        # Extract location information
        location_name = self._extract_location_name(offer)
        location_url = self._create_location_url(offer)

        # Format publication time
        published_time = self._format_publication_time(offer)

        return template.format(
            title=self._clean_html_text(offer.title or ""),
            description=self._clean_html_text(offer.description or ""),
            location_url=location_url,
            location_name=location_name,
            price=price,
            published_time=published_time,
        )

    def _extract_price(self, offer: Offer) -> str:
        if not offer.params:
            return "Цена не указана"

        price_params = [param for param in offer.params if param.key == "price"]
        if price_params and price_params[0].value.label:
            return price_params[0].value.label

        return "Цена не указана"

    def _extract_location_name(self, offer: Offer) -> str:
        if not offer.location:
            return "Локация не указана"

        city_name = (
            offer.location.city.name if offer.location.city else "Неизвестный город"
        )
        district_name = (
            offer.location.district.name
            if offer.location.district
            else "Неизвестный район"
        )

        return f"{city_name}/{district_name}"

    def _create_location_url(self, offer: Offer) -> str:
        if not offer.map or not offer.map.lat or not offer.map.lon:
            return "https://maps.google.com"

        return f"http://maps.google.com/maps?q=loc:{offer.map.lat},{offer.map.lon}"

    def _format_publication_time(self, offer: Offer) -> str:
        if not offer.last_refresh_time:
            return "Время не указано"

        try:
            timestamp = datetime.strptime(
                offer.last_refresh_time, "%Y-%m-%dT%H:%M:%S%z"
            )
            return timestamp.strftime("%H:%M | %d.%m.%Y")
        except ValueError:
            return "Время не указано"

    def _clean_html_text(self, text: str) -> str:
        if not text:
            return ""

        clean_parser = LexborHTMLParser(text)
        clean_text = clean_parser.text(strip=True, separator="\n")

        # Limit text length
        if len(clean_text) > MAX_DESCRIPTION_LENGTH:
            clean_text = clean_text[:MAX_DESCRIPTION_LENGTH] + "..."

        return clean_text

    def _create_offer_keyboard(self, offer: Offer) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        if offer.url:
            button = types.InlineKeyboardButton(
                "Объявления / E'lon 🔗", url=str(offer.url)
            )
            keyboard.add(button)
        return keyboard

    def _send_photo_message(
        self,
        caption: str,
        photo_path: Optional[Union[bytes, str]],
        reply_markup: types.InlineKeyboardMarkup,
    ) -> bool:
        try:
            photo: Union[str, types.InputFile]
            if isinstance(photo_path, str) and photo_path.startswith("https"):
                photo = photo_path
            else:
                photo = types.InputFile(io.BytesIO(photo_path.read()))  # type: ignore

            self.bot.send_photo(
                self.channel_id,
                caption=caption,
                photo=photo,
                reply_markup=reply_markup,
                timeout=10,
            )

            # Close file if it's a local file
            if (
                not isinstance(photo, str)
                and not isinstance(photo.file, str)
                and hasattr(photo.file, "close")
            ):
                photo.file.close()

            return True

        except Exception as e:
            logger.exception("Error sending photo message: %s" % e)
            return False

    def _send_text_message(
        self, text: str, reply_markup: types.InlineKeyboardMarkup
    ) -> bool:
        try:
            self.bot.send_message(
                self.channel_id,
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
            return True

        except Exception as e:
            logger.exception("Error sending text message: %s" % e)
            return False

    def _random_delay(self) -> None:
        delay = random.choice(MESSAGE_DELAY_SECONDS)
        time.sleep(delay)
