# -*- coding: utf-8 -*-
# !/usr/bin/python3


import json
import os
import logging
import traceback
import base64
import gpiozero
import datetime
from picamera2 import Picamera2
from Misc import get911


EMAIL_USER = get911('EMAIL_USER')
EMAIL_APPPW = get911('EMAIL_APPPW')
EMAIL_RECEIVER = get911('EMAIL_RECEIVER')
MAC_ADDR = get911('BLUETOOTH_ADDRESS')
NOW = datetime.datetime.now()
START_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 0, 30, 00)
END_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 8, 30, 00)
# START_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0)
# END_DATE = datetime.datetime(NOW.year, NOW.month, NOW.day, 23, 59, 59)

SCRIPT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)))
RECORDINGS_FOLDER = os.path.join(SCRIPT_FOLDER, "_RECORDINGS")
TODAY_FOLDER = os.path.join(RECORDINGS_FOLDER, "_TODAY")
REC_FILE = None

PIR = gpiozero.MotionSensor(26)


def on_motion():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("Motion detected!")

    # Rec for x seconds
    global REC_FILE
    REC_FILE = os.path.join(TODAY_FOLDER, now + ".mp4")
    with Picamera2() as camera:
        camera.configure(camera.create_video_configuration(main={"size": (1920, 1080)}))
        camera.start_and_record_video(REC_FILE, duration=10)


def off_motion():
    logger.info("Motion Stopped")

    # Run sendMail
    global SCRIPT_FOLDER
    cmd = " ".join(["python3", os.path.join(SCRIPT_FOLDER, "sendMail.py"), REC_FILE, "&"])
    os.system(cmd)

    logger.info("Waiting for motion")


def main():
    # Check if FOLDERS exist
    if not os.path.exists(RECORDINGS_FOLDER):
        os.mkdir(RECORDINGS_FOLDER)
    if not os.path.exists(TODAY_FOLDER):
        os.mkdir(TODAY_FOLDER)

    # GO GO GO
    logger.info("Waiting for motion")
    while True:
        PIR.when_motion = on_motion
        PIR.when_no_motion = off_motion


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Main
    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        logger.info("End")
