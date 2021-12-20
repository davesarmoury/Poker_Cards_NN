#!/usr/bin/env python3

from pyniryo import *
from threading import Thread, Lock
import pygame
import time
import random

robot_ip = "192.168.2.114"
grip_speed = 500

audio = {}
audio["startup"] = []
audio["startup"].append("turret_active_1.wav")
audio["startup"].append("turret_active_5.wav")
audio["startup"].append("turret_autosearch_1.wav")
audio["startup"].append("turret_pickup_2.wav")

audio["bet"] = []
audio["bet"].append("turret_active_3.wav")
audio["bet"].append("turret_deploy_3.wav")
audio["bet"].append("turret_disabled_1.wav")
audio["bet"].append("turret_pickup_2.wav")

audio["fold"] = []
audio["fold"].append("turret_disabled_3.wav")
audio["fold"].append("turret_disabled_1.wav")
audio["fold"].append("turret_disabled_4.wav")
audio["fold"].append("turret_pickup_10.wav")
audio["fold"].append("turret_retire_6.wav")
audio["fold"].append("turret_retire_7.wav")
audio["fold"].append("turretshotbylaser10.wav")

audio["win"] = []
audio["win"].append("turret_active_6.wav")
audio["win"].append("turret_disabled_1.wav")
audio["win"].append("turret_pickup_2.wav")
audio["win"].append("turret_retire_3.wav")
audio["win"].append("turret_retire_3.wav")
audio["win"].append("turret_retire_3.wav")

audio["lose"] = []
audio["lose"].append("turret_disabled_5.wav")
audio["lose"].append("turret_disabled_6.wav")
audio["lose"].append("turret_disabled_7.wav")
audio["lose"].append("turret_disabled_8.wav")
audio["lose"].append("turretshotbylaser09.wav")
audio["lose"].append("turretshotbylaser10.wav")
audio["lose"].append("turretwitnessdeath02.wav")
audio["lose"].append("turretwitnessdeath10.wav")

def playAudio(audio, type, dir, odds=70):
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
    global keep_camming, lock, new_frame, _frame

    w = 1280
    h = 720

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter("/home/davesarmoury/poker_video.mp4", fourcc, 30, (w, h))

    while keep_camming:
        ret_val, frame = cam.read()
        lock.acquire()
        _frame = frame
        new_frame = True
        lock.release()
        writer.write(frame)

    writer.release()

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
    global lock, _frame, new_frame
    lock.acquire()
    new_frame = False
    rframe = _frame.copy()
    lock.release()

    return rframe

def main():
    global keep_camming, lock, new_frame

    robot = initRobot(robot_ip)

    if robot:
        openGripper(robot)
        closeGripper(robot)

        new_frame = False
        keep_camming = True
        lock = Lock()
        cam_thread = Thread(target=cameraThread, args=())
        cam_thread.daemon = True
        cam_thread.start()

        while True:
            if new_frame:
                img = getFrame()
                cv2.imshow('Poker Cam', img)
                if cv2.waitKey(1) == 27:
                    break  # esc to quit
            time.sleep(0.01)

        keep_camming = False
        cv2.destroyAllWindows()
        robot.close_connection()
        time.sleep(1.0)
        print("Goodnight")

main()

