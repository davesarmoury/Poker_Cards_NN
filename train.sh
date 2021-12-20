#!/usr/bin/env bash

cd yolov5/
python3 train.py --img 576 --batch 16 --epochs 100 --data '../data.yaml' --cfg ../yolo.cfg --weights '' --name yolov5s_results  --cache
