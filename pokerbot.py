#!/usr/bin/env python3

import sys
from pyniryo import *
from threading import Thread, Lock
import pygame
import time
import random

import torch
import torch.backends.cudnn as cudnn

sys.path.insert(0, 'yolov5')
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression
from utils.torch_utils import select_device, time_synchronized

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from flask import Flask
from flask import request
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

robot_ip = "192.168.2.107"
grip_speed = 500

def playAudio(audio, type, dir="portal_turret_audio/audio/", odds=70):
    randval = random.randint(0, 100)
    if odds >= randval:
        pygame.mixer.music.load(dir + audio[type][random.randint(0, len(audio[type]) - 1)])
        pygame.mixer.music.play()

def openGripper(robot):
    robot.open_gripper(speed=grip_speed)

def closeGripper(robot):
    robot.close_gripper(speed=grip_speed)

def initRobot(ip):
    try:
        print("Connecting to " + ip)
        robot = NiryoRobot(ip)
        print("Connected")

        print("Starting Calibration")
        robot.calibrate_auto()
        robot.update_tool()
        robot.set_learning_mode(False)
        print("Calibration Complete")
        return robot

    except Exception as e:
        print("INIT ERROR: " + str(e))
        return None

def yoloThread():
    global shut_r_down, image_lock, new_frame, _frame

    device = select_device("")
    half = device.type != 'cpu'
    cudnn.benchmark = True

    model = attempt_load("best.pt", map_location=device)
    stride = int(model.stride.max())
    imgsz = 576
    if half:
        model.half()  # to FP16

    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

    while not shut_r_down:
        if new_frame:
            image_lock.acquire()
            frame = _frame.copy()
            new_frame = False
            image_lock.release()

            frame = frame[0:720, 280:280+720]
            frame = cv2.resize(frame, (imgsz, imgsz))
            frame = frame.transpose((2, 0, 1))
            img = torch.from_numpy(frame).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = model(img)[0]

            pred = non_max_suppression(pred, 0.4, 0.45)
            t2 = time_synchronized()

            s = ""
            for i, det in enumerate(pred):  # detections per image
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    print(f'{s}Done. ({t2 - t1:.3f}s)')

        time.sleep(0.002)

    print("Network Thread Closed")

def cameraThread():
    global shut_r_down, image_lock, new_frame, _frame

    w = 1280
    h = 720

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter("/home/davesarmoury/poker_video.mp4", fourcc, 30, (w, h))

    while not shut_r_down:
        ret_val, frame = cam.read()
        image_lock.acquire()
        _frame = frame
        new_frame = True
        image_lock.release()
        writer.write(frame)
        cv2.imshow('Poker Cam', _frame)
        cv2.waitKey(1)

    print("Closing video stream...")
    writer.release()
    print("Video Stream Closed")

def armThread():
    global shut_r_down, robot, current_bet, new_turn, new_hand, new_river

    while not shut_r_down:
        if new_hand:
            print("New Hand")
            new_hand = False
            update_hand(robot)
        if new_river:
            print("New River")
            new_river = False
            update_river(robot)
        if new_turn:
            print("New Turn")
            new_turn = False
            take_turn(robot, current_bet, hand, river)
        time.sleep(0.5)

    print("Disconnecting Robot...")
    robot.close_connection()
    print("Robot Disconnected")

def take_turn(robot, current_bet, hand, river):
    pass

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/quit")
def die():
    global shut_r_down
    print("Shutting Down...")
    shut_r_down = True
    pygame.mixer.quit()
    time.sleep(1.0)
    print("Goodnight")
    shutdown_server()
    return "Goodnight"

@app.route("/river")
def river():
    global new_river
    new_river = True
    return "Confirmed"

@app.route("/hand")
def hand():
    global new_hand
    new_hand = True
    return "Confirmed"

@app.route("/turn")
def turn():
    global current_bet, new_turn
    current_bet = int(request.args.get("current_bet"), 0)
    new_turn = True
    return "Confirmed"

@app.route("/lose")
def lose():
    playAudio(audio, "lose")
    return "Confirmed"

@app.route("/win")
def win():
    playAudio(audio, "win")
    return "Confirmed"

def bet(robot):
    playAudio(audio, "bet")
    pass

def fold(robot):
    playAudio(audio, "fold")
    pass

def show(robot):
    # Move arm
    # Grab cards
    # Move arm
    # Drop Cards
    pass

def update_river(robot):
    # Move arm
    # AI get 3-5 cards
    # Move arm
    pass

def update_hand(robot):
    # Move arm
    # AI get 2 cards
    # Move arm
    pass

def getFrame():
    global image_lock, _frame, new_frame
    image_lock.acquire()
    new_frame = False
    rframe = _frame.copy()
    image_lock.release()

    return rframe

def main():
    global shut_r_down, image_lock, new_turn, new_hand, new_river, robot

    current_bet = 0
    new_turn = False
    new_hand = False
    new_river = False
    shut_r_down = False

    audioFile = open("audio.yaml", 'r')
    audio = load(audioFile, Loader=Loader)
    audioFile.close()

    robot = initRobot(robot_ip)

    if robot:
        pygame.mixer.init()

        openGripper(robot)
        closeGripper(robot)

        image_lock = Lock()
        cam_thread = Thread(target=cameraThread, args=())
        cam_thread.daemon = True
        cam_thread.start()

        yolo_thread = Thread(target=yoloThread, args=())
        yolo_thread.daemon = True
        yolo_thread.start()

        arm_thread = Thread(target=armThread, args=())
        arm_thread.daemon = True
        arm_thread.start()

        playAudio(audio, "startup", odds=100)

        app.run("0.0.0.0")

main()
