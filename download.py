# Inspired by https://github.com/avaapm/marveldataset2016/blob/master/MARVEL_Download.py

import os
import json
from multiprocessing import Pool as ThreadPool
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import re

from bs4 import BeautifulSoup
import tqdm

SAVE_PHOTOGRAPHER = 0 # Set SAVE_PHOTOGRAPHER = 1, if you also want to save the photographer of each image
NUMBER_OF_WORKERS = 10 # Number of threads for download
FILE_TO_DOWNLOAD_FROM = "metadata.json" # Name of GT file, to get IDs from
SOURCE_LINK = "https://www.shipspotting.com/photos/"
IMAGE_DIR = os.path.join(os.getcwd(), "data", "images")
META_DIR = os.path.join(os.getcwd(), "data", "metadata")


def download_image(file_id: str):
    """This function downloads an image from a given URL and saves it
    to a specified directory. It also saves the author's name in a text
    file if specified. If the image was deleted on the original website, 
    this image will be skipped and nothing will be downloaded or saved.
    
    Args:
        file_id (str): The ID of the file to retrieve the image from.
    """
    try:
        url = SOURCE_LINK + file_id
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req, timeout=300).read()
        soup = BeautifulSoup(html, "lxml")

        images = [img for img in soup.findAll("img")]
        image_links = [each.get("src") for each in images]

        for image_link in image_links:
            if image_link is not None:
                if "http" in image_link and "jpg" in image_link and "photos/big" in image_link:
                    filename = image_link.split("/")[-1].split("?")[0]
                    req = Request(image_link, headers={"User-Agent": "Mozilla/5.0"})
                    web_file = urlopen(req, timeout=300)
                    with open(os.path.join(IMAGE_DIR, filename), "wb") as image_file:
                        image_file.write(web_file.read())
                    break

        if SAVE_PHOTOGRAPHER:
            data_script = soup.find("script", string=re.compile("INITIAL_DATA"))
            image_data = json.loads(
                data_script.text.split("window._INITIAL_DATA =")[1].strip()[:-1]
            )
            with open(
                os.path.join(META_DIR, file_id + ".txt"), "w", encoding="utf-8"
            ) as text_file:
                text_file.write(image_data["page_data"]["print_photographer"])

    except HTTPError:
        # Image was deleted
        pass


def main():
    with open(FILE_TO_DOWNLOAD_FROM, "r", encoding="utf-8") as annotation_file:
        annotation_data = json.load(annotation_file)

    image_ids = [entry["image_id"] for entry in annotation_data]

    # Make dir for images files
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # Make dir for images files
    if not os.path.exists(META_DIR) and SAVE_PHOTOGRAPHER:
        os.makedirs(META_DIR)

    # Only download files that are not there
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
