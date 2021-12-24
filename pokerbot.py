#!/usr/bin/env python3

import sys
from pyniryo import *
from threading import Thread, Lock
import pygame
import time
import random
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
    global shut_r_down, robot, current_bet, new_turn, new_deal

    while not shut_r_down:
        if new_deal:
            print("New Deal")
            new_deal = False
        if new_turn:
            print("New Turn")
            new_turn = False

    print("Disconnecting Robot...")
    robot.close_connection()
    print("Robot Disconnected")

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

@app.route("/deal")
def new_deal():
    global new_deal
    new_deal = True
    return "Confirmed"

@app.route("/turn")
def new_turn():
    global current_bet, new_turn
    current_bet = int(request.args.get("current_bet"))
    new_turn = True
    return "Confirmed"

def bet(robot):
    pass

def draw(robot):
    pass

def show(robot):
    pass

def fold(robot):
    pass

def river(robot):
    pass

def getFrame():
    global image_lock, _frame, new_frame
    image_lock.acquire()
    new_frame = False
    rframe = _frame.copy()
    image_lock.release()

    return rframe

def main():
    global shut_r_down, image_lock, new_frame, robot

    new_frame = False
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

        arm_thread = Thread(target=armThread, args=())
        arm_thread.daemon = True
        arm_thread.start()

        playAudio(audio, "startup", odds=100)

        app.run("0.0.0.0")

main()
