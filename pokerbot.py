#!/usr/bin/env python3

from pyniryo import *
from threading import Thread, Lock
import time

robot_ip = "192.168.2.114"
grip_speed = 500

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

    cam = cv2.VideoCapture(0)
    while keep_camming:
        ret_val, frame = cam.read()
        lock.acquire()
        _frame = frame
        new_frame = True
        lock.release()

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

