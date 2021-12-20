#!/usr/bin/env bash

sudo apt install -y curl unzip

curl -L "https://universe.roboflow.com/ds/uE9csFp97l?key=mDADCSXlus" > roboflow.zip
unzip roboflow.zip
rm roboflow.zip

cd yolov5
pip3 install -r requirements.txt

cd ..

python3 preprocess.py
