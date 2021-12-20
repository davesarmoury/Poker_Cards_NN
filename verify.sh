#!/usr/bin/env bash

cd yolov5
python3 detect.py --weights runs/train/exp/weights/best.pt --img 576 --conf 0.5 --source ../test/images
