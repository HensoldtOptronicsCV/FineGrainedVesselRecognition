# MIT License
#
# Copyright (c) 2024 HENSOLDT Optronics Computer Vision
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Inspired by https://github.com/avaapm/marveldataset2016/blob/master/MARVEL_Download.py

import json
import os
import re
import time
from http.client import IncompleteRead
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import tqdm
from bs4 import BeautifulSoup

SAVE_PHOTOGRAPHER = 0  # Set SAVE_PHOTOGRAPHER = 1, if you also want to save the photographer of each image
NUMBER_OF_WORKERS = 10  # Number of threads for download
FILE_TO_DOWNLOAD_FROM = "metadata.json"  # Name of GT file, to get IDs from
SOURCE_LINK = "https://www.shipspotting.com/photos/"
IMAGE_DIR = os.path.join(os.getcwd(), "data", "images")
META_DIR = os.path.join(os.getcwd(), "data", "metadata")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.shipspotting.com/",
}
DOWNLOAD_TIMEOUT = 30
PAGE_TIMEOUT = 20
MAX_RETRIES = 4


def download_image(file_id: str):
    """This function downloads an image from a given URL and saves it to a specified directory. It also saves the
    author's name in a text file if specified. If the image was deleted on the original website, this image will
    be skipped and nothing will be downloaded or saved.

    Args:
        file_id (str): The ID of the file to retrieve the image from.
    """
    image_url = f"https://www.shipspotting.com/photos/big/{file_id[-1]}/{file_id[-2]}/{file_id[-3]}/{file_id}.jpg?cb=0"

    image_path = os.path.join(IMAGE_DIR, file_id + ".jpg")
    meta_path = os.path.join(META_DIR, file_id + ".txt")

    # Always initialise this.
    photographer = None

    # --------------------------------------------------
    # Try to retrieve photographer
    # --------------------------------------------------
    if SAVE_PHOTOGRAPHER:
        try:
            page_url = SOURCE_LINK + file_id
            req = Request(page_url, headers=HEADERS)

            with urlopen(req, timeout=PAGE_TIMEOUT) as response:
                html = response.read()

            soup = BeautifulSoup(html, "lxml")
            page_text = soup.get_text(" ", strip=True)

            # Only treat an explicit deletion message as deleted.
            if re.search(
                r"\bphoto\s+(?:has\s+been\s+)?deleted\b",
                page_text,
                flags=re.IGNORECASE,
            ):
                tqdm.tqdm.write(f"Image ID {file_id}: photo was deleted")

                if os.path.exists(image_path):
                    os.remove(image_path)

                if os.path.exists(meta_path):
                    os.remove(meta_path)

                return

            # Extract photographer from rendered page text.
            #
            # Example:
            # Photographer: John Smith Captured: ...
            #
            # Stop at the next known metadata field.
            match = re.search(
                r"\bPhotographer\s*:\s*(.+?)"
                r"(?=\s+(?:Captured|Title|Location|"
                r"Photo Category|Added|IMO|MMSI|Vessel)\s*:|$)",
                page_text,
                flags=re.IGNORECASE,
            )

            if match:
                photographer = match.group(1).strip()

                # Remove profile text if it is included.
                photographer = re.sub(
                    r"\s*(?:\[?\s*View profile\s*\]?)\s*$",
                    "",
                    photographer,
                    flags=re.IGNORECASE,
                ).strip()

            if not photographer:
                tqdm.tqdm.write(f"Image ID {file_id}: photographer not found; downloading image anyway")

        except Exception as e:
            # Photographer metadata is optional.
            # Do NOT abort the image download here.
            tqdm.tqdm.write(
                f"Image ID {file_id}: could not retrieve photographer: "
                f"{type(e).__name__}: {e}; "
                f"downloading image anyway"
            )
            photographer = None

    # --------------------------------------------------
    # Download image
    # --------------------------------------------------
    download_successful = False

    for attempt in range(MAX_RETRIES):
        try:
            req = Request(image_url, headers=HEADERS)

            with urlopen(req, timeout=DOWNLOAD_TIMEOUT) as response:
                content_type = response.headers.get("Content-Type", "")
                data = response.read()

            # Sometimes an HTML error page is returned with HTTP 200.
            if not content_type.lower().startswith("image/"):
                tqdm.tqdm.write(f"Image ID {file_id}: unavailable (server returned {content_type})")
                return

            # Verify JPEG magic bytes.
            if not data.startswith(b"\xff\xd8"):
                tqdm.tqdm.write(f"Image ID {file_id}: invalid JPEG, skipping")
                return

            with open(image_path, "wb") as image_file:
                image_file.write(data)

            download_successful = True
            break

        except HTTPError as e:
            if e.code in (404, 410):
                tqdm.tqdm.write(f"Image ID {file_id}: image was deleted")
                return

            if e.code in (403, 429, 500, 502, 503, 504):
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
                    continue

            tqdm.tqdm.write(f"Image ID {file_id}: HTTP {e.code}")
            return

        except (IncompleteRead, URLError, TimeoutError) as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2**attempt)
                continue

            tqdm.tqdm.write(
                f"Image ID {file_id}: image download failed after {MAX_RETRIES} attempts: {type(e).__name__}: {e}"
            )
            return

        except Exception as e:
            tqdm.tqdm.write(f"Image ID {file_id}: {type(e).__name__}: {e}")
            return

    # --------------------------------------------------
    # Save photographer only after successful download
    # --------------------------------------------------
    if download_successful and SAVE_PHOTOGRAPHER and photographer:
        try:
            with open(
                meta_path,
                "w",
                encoding="utf-8",
            ) as text_file:
                text_file.write(photographer)

        except OSError as e:
            tqdm.tqdm.write(f"Image ID {file_id}: image downloaded, but photographer could not be saved: {e}")


def main():
    with open(FILE_TO_DOWNLOAD_FROM, encoding="utf-8") as annotation_file:
        annotation_data = json.load(annotation_file)

    image_ids = [entry["image_id"] for entry in annotation_data]

    # Make dir for image files
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # Make dir for text files
    if not os.path.exists(META_DIR) and SAVE_PHOTOGRAPHER:
        os.makedirs(META_DIR)

    # Remove files left behind by older failed downloads
    for file in Path(IMAGE_DIR).glob("*.jpg"):
        if file.stat().st_size == 0:
            file.unlink()

    downloaded_ids = [file.stem for file in Path(IMAGE_DIR).glob("*.jpg")]

    image_ids = list(set(image_ids) - set(downloaded_ids))

    # Make the pool of workers
    pool = ThreadPool(NUMBER_OF_WORKERS)

    # Open the URLs in their own threads and save the images
    for _ in tqdm.tqdm(
        pool.imap_unordered(download_image, image_ids),
        total=len(image_ids),
    ):
        pass

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
