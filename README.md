# Towards Explainable Visual Vessel Recognition Using Fine-Grained Classification and Image Retrieval

This repository shows how to download the Military MARVEL Dataset and sort it by class or superclass.

Here is the direct link to the paper: [click me](https://openaccess.thecvf.com/content/CVPR2024W/TCV2024/html/Karus_Towards_Explainable_Visual_Vessel_Recognition_Using_Fine-Grained_Classification_and_Image_CVPRW_2024_paper.html)

The code can be excecuted using Python3.10, the dependencies can be found in `requirements.txt` and they can be installed using:

```
pip install -r requirements.txt
```

## Downloading Military MARVEL dataset
In order to download the Military MARVEL dataset, run the following command:
```
python download.py
```

## Sort images by class or superclass:
In order to sort the images of the Military MARVEL dataset, run the following command:
```
python sort_by.py
```
This will create folders for each unique class and puts the corresponding images in it. The structure can be used by `ImageFolder` class of PyTorch. Set `SORT_BY = "class"` if you want to create the fine-grained dataset with 137 classes and `SORT_BY = "superclass"` to create the less fine-grained dataset with 11 classes. The file structure of the GT file `metadata.json` looks as follows:
```json
[{"image_id": "1337893", "superclass": "Auxiliaries", "class": "Schwedeneck class"}, {...}]
```

## Cite us

If you use Military MARVEL in your research, please cite:

```
@InProceedings{Karus_2024_CVPR,
    author    = {Karus, Heiko and Schwenker, Friedhelm and Munz, Michael and Teutsch, Michael},
    title     = {Towards Explainable Visual Vessel Recognition Using Fine-Grained Classification and Image Retrieval},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops},
    month     = {June},
    year      = {2024},
    pages     = {82-92}
}
```
