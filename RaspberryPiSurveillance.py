# -*- coding: utf-8 -*-
# !/usr/bin/python3


import datetime
import json
import os
import logging
import random
import traceback
import time
import signal
import sys
from PIL import Image
from Misc import get911, sendEmail
from gpiozero import MotionSensor
from moviepy.editor import VideoFileClip
from picamera2 import Picamera2
from sense_hat import SenseHat


def signal_handler(sig, frame):
    if sig == signal.SIGTERM:
        logger.info("Script terminated by SIGTERM")
        sense.clear()
        sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)


def on_motion():
    """Callback function when motion is detected.

    This function is called when the motion sensor detects motion.
    It lights the SenseHat Matrix and records a VIDEO_DURATION-second video and saves it to the
    RECORDINGS_FOLDER with a filename based on the current date and time.
    """
    logger.info("Motion detected!")

    global VIDEO_FILE, RECORDING

    # Light the matrix
    if not STEALTH_MODE:
        whiteMatrix = [(255, 255, 255) for _ in range(64)]
        sense.set_pixels(whiteMatrix)

    timestamp = datetime.datetime.now().strftime("%H-%M-%S")
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    VIDEO_FILE = os.path.join(RECORDINGS_FOLDER, day, day + "_" + timestamp + ".mp4")

    # Create day_folder if not exists
    day_folder = os.path.dirname(VIDEO_FILE)
    if not os.path.exists(day_folder):
        os.mkdir(day_folder)

    # Record
    RECORDING = True
    logger.info("Recording video to " + os.path.basename(VIDEO_FILE))
    camera.configure(camera.create_video_configuration(main={"size": VIDEO_SIZE}))
    camera.start_and_record_video(VIDEO_FILE, duration=VIDEO_DURATION)


def off_motion():
    """Callback function when motion is no longer detected.

    This function is called when the motion sensor stops detecting motion.
    It stops the video recording, turns of the SenseHat Matrix sends an email notification with the
    video timestamp to the specified receiver, and generates a thumbnail image from the recorded video.
    """

    global VIDEO_FILE, RECORDING

    logger.info("No motion detected.")
    camera.stop_recording()
    sense.clear()
    RECORDING = False
    logger.info("Video recording stopped.")

    VIDEO_DATE = os.path.basename(VIDEO_FILE).replace(".mp4", "")
    sendEmail("EYE - " + VIDEO_DATE, "Motion detected at " + VIDEO_DATE)
    logger.info("Email notification sent successfully.")

    # Generate thumbnail
    with VideoFileClip(VIDEO_FILE) as clip:
        thumbnail_img = Image.fromarray(clip.get_frame(random.random() * clip.duration))
        thumbnail_img.thumbnail((int(clip.w / (clip.h / 240)), int(clip.h / (clip.h / 240))))
        thumbnail_img.save(VIDEO_FILE.replace(".mp4", ".png"), optimize=True)
    logger.info("Thumbnail Generated")


def getCorner(x, y):
    """
    Get the next corner coordinates in a circular pattern.

    Args:
        x (int): Current x-coordinate.
        y (int): Current y-coordinate.

    Returns:
        Tuple[int, int]: New x and y coordinates representing the next corner.
    """
    if x == 0 and y == 0:
        x = 7
    elif x == 7 and y == 0:
        y = 7
    elif x == 7 and y == 7:
        x = 0
    else:
        y = 0

    return x, y


def main():
    """Main function for motion detection.

    This function sets up the motion_sensor object to call the on_motion() and off_motion() callback functions
    when motion is detected and when motion stops, respectively. It then enters a loop to continuously check for
    motion while the script is running.
    """

    logger.info("Motion detection program started")
    sense.clear()
    motion_sensor = MotionSensor(MOTION_SENSOR_GPIO_PIN)
    counter, x, y = 0, 0, 0

    while True:

        # Light corner
        if not RECORDING:
            if counter % 2 == 0:
                x, y = getCorner(x, y)
                sense.set_pixel(x, y, (255, 0, 0))
            else:
                sense.clear()

        # Check for motion
        motion_sensor.when_motion = on_motion
        motion_sensor.when_no_motion = off_motion

        # You can add other code or actions here while the motion detection runs.
        time.sleep(1)  # Pause to reduce CPU usage

        counter += 1


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
    RECORDING = False
    VIDEO_FILE = ""
    VIDEO_SIZE = (config["VIDEO_WIDTH"], config["VIDEO_HEIGHT"])
    VIDEO_DURATION = config["VIDEO_DURATION"]
    camera = Picamera2()

    # Create sense hat
    sense = SenseHat()
    STEALTH_MODE = config["STEALTH_MODE"]

    # Main
    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        sense.clear()
        logger.info("End")
