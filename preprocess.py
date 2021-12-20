#!/usr/bin/env python3

import cv2
import os
from tqdm import tqdm

old_size = 600
new_size = 576
scale = new_size / old_size

def scale_images(dir):
    filenames = os.listdir(dir)
    for fname in tqdm(filenames, desc=dir):
        img = cv2.imread(dir + fname)
        img = cv2.resize(img, [new_size, new_size])
        cv2.imwrite(dir + fname, img)

def scale_labels(dir):
    filenames = os.listdir(dir)
    for fname in tqdm(filenames, desc=dir):
        inFile = open(dir + fname, 'r')
        lines = inFile.readlines()
        inFile.close()

        outFile = open(dir + fname, 'w')
        for line in lines:
            data = line.split(" ")
            newLine = data[0]
            newLine += " " + str(float(data[1]) * scale)
            newLine += " " + str(float(data[2]) * scale)
            newLine += " " + str(float(data[3]) * scale)
            newLine += " " + str(float(data[4]) * scale)
            outFile.write(newLine + "\n")
        outFile.close()

scale_images("test/images/")
scale_labels("test/labels/")
scale_images("train/images/")
scale_labels("train/labels/")
scale_images("valid/images/")
scale_labels("valid/labels/")
