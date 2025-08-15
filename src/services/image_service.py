import concurrent.futures
import math
import os
import random
import shutil
from contextlib import suppress
from os import walk
from os.path import join
from typing import Optional

import requests
from loguru import logger
from photocollage import render
from photocollage.collage import Page, Photo

from ..core.config import (
    COLLAGE_BORDER_WIDTH,
    COLLAGE_OUTPUT_HEIGHT,
    COLLAGE_OUTPUT_WIDTH,
    DOWNLOADS_DIR,
    MAX_ASPECT_RATIO,
    MAX_DOWNLOAD_WORKERS,
    PHOTO_COLLAGE_DIR,
    TEMP_PHOTOS_PREFIX,
)


class ImageProcessor:

    def __init__(self) -> None:
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(PHOTO_COLLAGE_DIR, exist_ok=True)

    def create_photo_collage(
        self, image_urls: list[str], offer_id: int
    ) -> Optional[str]:
        if not image_urls:
            logger.warning("No images provided for offer %s" % offer_id)
            return None

        temp_folder = os.path.join(DOWNLOADS_DIR, f"{TEMP_PHOTOS_PREFIX}{offer_id}")

        try:
            if not self._download_images(image_urls, temp_folder):
                logger.error("Failed to download images for offer %s" % offer_id)
                return None

            image_files = self._get_image_files(temp_folder)
            if not image_files:
                logger.warning("No valid images found for offer %s" % offer_id)
                return None

            photo_list = render.build_photolist(image_files)
            filtered_photos = self._filter_photos_by_aspect_ratio(photo_list)

            if not filtered_photos:
                logger.warning(
                    "No suitable photos after filtering for offer %s" % offer_id
                )
                return None

            output_path = os.path.join(PHOTO_COLLAGE_DIR, f"collage-{offer_id}.jpg")
            return self._generate_collage(output_path, filtered_photos)

        except Exception as e:
            logger.error("Error creating collage for offer %s: %s" % (offer_id, e))
            return None
        finally:
            with suppress(Exception):
                shutil.rmtree(temp_folder)
                logger.debug("Cleaned up temp folder for offer %s" % offer_id)

    def _download_images(self, urls: list[str], output_folder: str) -> bool:
        if not urls:
            return False

        os.makedirs(output_folder, exist_ok=True)

        success = True
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_DOWNLOAD_WORKERS
        ) as executor:
            futures = [
                executor.submit(self._download_single_image, url, output_folder)
                for url in urls
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.warning("Failed to download image: %s" % e)
                    success = False

        return success

    def _download_single_image(self, url: str, output_folder: str) -> None:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            filename = f"{url.split('/')[-2]}.jpg"
            file_path = os.path.join(output_folder, filename)

            with open(file_path, "wb") as f:
                f.write(response.content)

        except requests.RequestException as e:
            logger.warning("Failed to download image from %s: %s" % (url, e))
            raise

    def _get_image_files(self, folder: str) -> list[str]:
        return [
            join(root, file)
            for root, _, files in walk(folder)
            for file in files
            if file.lower().endswith(".jpg")
        ]

    def _filter_photos_by_aspect_ratio(self, photos: list[Photo]) -> list[Photo]:
        filtered = []
        for photo in photos:
            aspect_ratio = float(photo.w) / float(photo.h)
            if aspect_ratio <= MAX_ASPECT_RATIO:
                filtered.append(photo)
            else:
                logger.debug("Filtered out photo with aspect ratio %.2f" % aspect_ratio)
        return filtered

    def _generate_collage(self, output_path: str, photos: list[Photo]) -> str:
        # Calculate optimal grid layout
        ratio = COLLAGE_OUTPUT_HEIGHT / COLLAGE_OUTPUT_WIDTH
        avg_ratio = sum(photo.h / photo.w for photo in photos) / len(photos)
        virtual_image_count = 2 * len(photos)
        columns = int(round(math.sqrt(avg_ratio / ratio * virtual_image_count)))

        # Create page and add photos
        page = Page(1.0, ratio, columns)
        random.shuffle(photos)

        for photo in photos:
            page.add_cell(photo)

        # Adjust layout and scaling
        page.adjust()
        page.target_ratio = COLLAGE_OUTPUT_HEIGHT / COLLAGE_OUTPUT_WIDTH
        page.adjust_cols_heights()
        page.scale_to_fit(COLLAGE_OUTPUT_WIDTH, COLLAGE_OUTPUT_HEIGHT)

        enlargement = float(COLLAGE_OUTPUT_WIDTH) / page.w
        page.scale(enlargement)

        # Create rendering task
        border_width = COLLAGE_BORDER_WIDTH * max(page.w, page.h)
        # border_color = render.random_color()

        task = render.RenderingTask(
            page=page,
            output_file=output_path,
            border_width=border_width,
            border_color=(255, 255, 255),
        )
        task.run()

        return str(task.output_file)
