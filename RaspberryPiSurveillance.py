# -*- coding: utf-8 -*-
# !/usr/bin/python3


import datetime
import json
import os
import logging
import random
import traceback
from PIL import Image
from Misc import get911, sendEmail
from gpiozero import MotionSensor
from moviepy.editor import VideoFileClip
import time
from picamera2 import Picamera2


def on_motion():
    """Callback function when motion is detected.

    This function is called when the motion sensor detects motion. It records a 5-second video and saves it
    to the RECORDINGS_FOLDER with a filename based on the current date and time.

    """
    logger.info("Motion detected!")

    global REC_FILE
    timestamp = datetime.datetime.now().strftime("%H-%M-%S")
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    REC_FILE = os.path.join(RECORDINGS_FOLDER, day, day + "_" + timestamp + ".mp4")

    # Create day_folder if not exists
    day_folder = os.path.dirname(REC_FILE)
    if not os.path.exists(day_folder):
        os.mkdir(day_folder)

    # Record
    logger.info("Recording video to " + os.path.basename(REC_FILE))
    camera.configure(camera.create_video_configuration(main={"size": REC_SIZE}))
    camera.start_and_record_video(REC_FILE, duration=10)


def off_motion():
    """Callback function when motion is no longer detected.

    This function is called when the motion sensor stops detecting motion. It stops the video recording, sends
    an email notification with the video timestamp to the specified receiver, and generates a thumbnail image
    from the recorded video.

    """
    logger.info("No motion detected.")
    camera.stop_recording()
    logger.info("Video recording stopped.")

    global REC_FILE
    REC_DATE = os.path.basename(REC_FILE).replace(".mp4", "")
    sendEmail("EYE - " + REC_DATE, "Motion detected at " + REC_DATE)
    logger.info("Email notification sent successfully.")

    # Generate thumbnail
    with VideoFileClip(REC_FILE) as clip:
        thumbnail_img = Image.fromarray(clip.get_frame(random.random() * clip.duration))
        thumbnail_img.thumbnail((int(clip.w / (clip.h / 240)), int(clip.h / (clip.h / 240))))
        thumbnail_img.save(REC_FILE.replace(".mp4", ".png"), optimize=True)


def main():
    """Main function for motion detection.

    This function sets up the motion_sensor object to call the on_motion() and off_motion() callback functions
    when motion is detected and when motion stops, respectively. It then enters a loop to continuously check for
    motion while the script is running.

    """

    logger.info("Motion detection program started")
    motion_sensor = MotionSensor(MOTION_SENSOR_GPIO_PIN)
    while True:
        motion_sensor.when_motion = on_motion
        motion_sensor.when_no_motion = off_motion

        # You can add other code or actions here while the motion detection runs.
        time.sleep(1)  # Pause to reduce CPU usage


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Load Config File
    configFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(configFile, "r") as inFile:
        config = json.loads(inFile.read())

    # Define the script's and recording folder paths
    SCRIPT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    RECORDINGS_FOLDER = os.path.join(SCRIPT_FOLDER, "_RECORDINGS")

    # Use MotionSensor if available, else use BasicSystem
    MOTION_SENSOR_GPIO_PIN = config["MOTION_SENSOR_GPIO_PIN"]

    # Create a PiCamera object
    logger.info("Setting PiCamera")
    REC_SIZE = (config["VIDEO_WIDTH"], config["VIDEO_HEIGHT"])
    REC_FILE = ""
    camera = Picamera2()
    Picamera2.set_logging(Picamera2.WARNING)

    # Main
    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
