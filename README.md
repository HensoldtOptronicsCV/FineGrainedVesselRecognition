# Towards Explainable Visual Vessel Recognition Using Fine-Grained Classification and Image Retrieval

This repository shows how to download the Military MARVEL Dataset and sort it by class or superclass.

Here is the direct link to the paper:\
TODO

The code can be excecuted using Python3.10, the dependencies can be found in `requirements.txt` and they can be installed using:

```
pip install -r requirements.txt
```

Downloading Military MARVEL dataset:
> In order to download the Military MARVEL dataset, download.py a Python script must be run.

Sort images by class or superclass:
> In order to sort the images of the Military MARVEL dataset, sort_by.py a Python script must be run. Set `SORT_BY = "class"` if you want to create the fine-grained dataset with 137 classes and `SORT_BY = "superclass"` to create the less fine-grained dataset with 11 classes.
> The file structure of the GT file `metadata.json` looks as follows:
```json
[{"image_id": "1337893", "superclass": "Auxiliaries", "class": "Schwedeneck class"}, {...}]
```

## Cite us

If you use Military MARVEL in your research, please cite:

```
@InProceedings{KarusCVPRW2024,   
Title = {{Towards Explainable Visual Vessel Recognition Using Fine-Grained Classification and Image Retrieval}},   
Author = {Heiko Karus and Friedhelm Schwenker and Michael Munz and Michael Teutsch},   
Booktitle = {IEEE CVPR Workshops},   
Year = {2024}   
}
```
