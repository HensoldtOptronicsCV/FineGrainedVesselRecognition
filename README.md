# FineGrainedVesselRecognition

This repository shows how to download the Military MARVEL Dataset and sorty it by class or superclass.

Here are the direct links to the papers:\
TODO

The code can be excecuted using Python3.10 and the dependencies can be found in requirments.txt.

Downloading Military MARVEL dataset:
 In order to download the Military MARVEL dataset, download.py a Python script must be run. Set `SAVE_PHOTOGRAPHER = 1` if
 you also want to save the photographer of each image.

Sort images by class or superclass:
 In order to sort the images of the Military MARVEL dataset, sort_by.py a Python script must be run. Set `SORT_BY = "class"` if you want to create the fine-grained dataset with 137 classes and `SORT_BY = "superclass"` to create the less fine-grained dataset with 11 classes.

## Cite us

If you use Military MARVEL in your research, please cite:

"`@InProceedings{KarusCVPRW2024,   
   Title = {{Towards Explainable Visual Vessel Recognition Using Fine-Grained Classification and Image Retrieval}},   
   Author = {Heiko Karus and Friedhelm Schwenker and Michael Munz and Michael Teutsch},   
   Booktitle = {IEEE CVPR Workshops},   
   Year = {2024}   
}`"
