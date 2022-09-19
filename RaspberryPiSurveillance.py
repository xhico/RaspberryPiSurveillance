# -*- coding: utf-8 -*-
# !/usr/bin/python3


import json
import os
import time

import gpiozero
import datetime
from picamera2 import Picamera2


def get911(key):
    with open('/home/pi/.911') as f:
        data = json.load(f)
    return data[key]


EMAIL_USER = get911('EMAIL_USER')
EMAIL_APPPW = get911('EMAIL_APPPW')
EMAIL_RECEIVER = get911('EMAIL_RECEIVER')
MAC_ADDR = get911('BLUETOOTH_ADDRESS')
NOW = datetime.datetime.now()
START_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 1, 30, 00)
END_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 8, 30, 00)
# START_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0)
# END_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 23, 59, 59)

SCRIPT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(SCRIPT_FOLDER, os.path.basename(os.path.abspath(__file__)).replace(".py", ".log"))
RECORDINGS_FOLDER = os.path.join(SCRIPT_FOLDER, "_RECORDINGS")
TODAY_FOLDER = os.path.join(RECORDINGS_FOLDER, "_TODAY")
REC_FILE = None

PIR = gpiozero.MotionSensor(26)


def writeLog(line):
    print(line)
    with open(LOG_FILE, "a") as outFile:
        outFile.write(line + "\n")


def on_motion():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    writeLog(now + " " + "Motion detected!")

    # Rec for x seconds
    global REC_FILE
    REC_FILE = os.path.join(TODAY_FOLDER, now + ".mp4")
    with Picamera2() as camera:
        camera.start_and_record_video(REC_FILE, duration=10)


def off_motion():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    writeLog(now + " " + "Motion Stopped\n")

    # Run sendMail
    sendMail_LOG_FILE = os.path.join(SCRIPT_FOLDER, "sendMail.log")
    cmd = " ".join(["python3", os.path.join(SCRIPT_FOLDER, "sendMail.py"), REC_FILE, ">>", sendMail_LOG_FILE, "&"])
    os.system(cmd)

    writeLog("Waiting for motion\n")


def main():
    # Check if FOLDERS exist
    if not os.path.exists(RECORDINGS_FOLDER):
        os.mkdir(RECORDINGS_FOLDER)
    if not os.path.exists(TODAY_FOLDER):
        os.mkdir(TODAY_FOLDER)

    # GO GO GO
    writeLog("Waiting for motion\n")
    while True:
        PIR.when_motion = on_motion
        PIR.when_no_motion = off_motion


if __name__ == '__main__':
    # Init
    writeLog("----------------------------------------------------")
    writeLog(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # Main
    try:
        main()
    except Exception as ex:
        print(ex)
    finally:
        print("End")
