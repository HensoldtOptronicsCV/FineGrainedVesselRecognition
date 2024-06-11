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


import os
import sys
from pathlib import Path
import json
import shutil


SORT_BY = "class"  # Set SORT_BY to "class" in order to get fine-grained dataset with 137 classes and "superclass" to get dataset with 11 classes.
FILE_TO_DOWNLOAD_FROM = "metadata.json" # GT file
IMAGE_DIR = os.path.join(os.getcwd(), "data", "images")


def create_sorted_dataset(downloaded_ids: list[str], annotation_data: list[dict[str, str]], dataset_folder: str):
    """The create_sorted_dataset function loops through each image_id in downloaded_ids and searches for the
    corresponding image_data in annotation_data. If the image_data is found, it creates a directory with the
    name of the category in the dataset_folder if it doesn't already exist. It then copies the image file from
    the IMAGE_DIR to the newly created category directory.

    Args:
        downloaded_ids (list[str]): A list of image IDs that have been downloaded.
        annotation_data (list[dict[str, str]]): A list of dictionaries containing annotation data for each image.
        dataset_folder (str): The path to the folder where the sorted dataset will be created.
    """
    for image_id in downloaded_ids:
        image_data = next(
            (item for item in annotation_data if item["image_id"] == image_id), None
        )
        if image_data is not None:
            category = image_data[SORT_BY]
            category_dir = os.path.join(dataset_folder, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)

            shutil.copy(
                os.path.join(IMAGE_DIR, image_id + ".jpg"),
                os.path.join(category_dir, image_id + ".jpg"),
            )


def main():
    downloaded_ids = [file.stem for file in Path(IMAGE_DIR).glob("*.jpg")]

    with open(FILE_TO_DOWNLOAD_FROM, "r", encoding="utf-8") as annotation_file:
        annotation_data = json.load(annotation_file)

    dataset_folder = IMAGE_DIR.replace("images", SORT_BY + "_dataset")

    if os.path.isdir(dataset_folder):
        sys.exit("Dataset already exists, please delete it!")

    os.makedirs(dataset_folder)

    create_sorted_dataset(downloaded_ids, annotation_data, dataset_folder)


if __name__ == "__main__":
    main()
