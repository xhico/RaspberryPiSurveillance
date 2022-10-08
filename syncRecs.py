# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import datetime
import traceback
import logging
import psutil
import yagmail

import RaspberryPiSurveillance

EMAIL_USER = RaspberryPiSurveillance.EMAIL_USER
EMAIL_RECEIVER = RaspberryPiSurveillance.EMAIL_RECEIVER
EMAIL_APPPW = RaspberryPiSurveillance.EMAIL_APPPW
MAC_ADDR = RaspberryPiSurveillance.MAC_ADDR
START_DATE = RaspberryPiSurveillance.START_DATE
END_DATE = RaspberryPiSurveillance.END_DATE
RECORDINGS_FOLDER = RaspberryPiSurveillance.RECORDINGS_FOLDER
TODAY_FOLDER = RaspberryPiSurveillance.TODAY_FOLDER
SCRIPT_FOLDER = RaspberryPiSurveillance.SCRIPT_FOLDER


def runMain():
    cmd = " ".join(["python3", os.path.join(SCRIPT_FOLDER, "RaspberryPiSurveillance.py"), ">", "/dev/null", "&"])
    os.system(cmd)


def killMain(procs):
    for proc in procs:
        proc.kill()


def main():
    # Check if FOLDERS exist
    logger.info("Check RECORDINGS_FOLDER && TODAY_FOLDER")
    if not os.path.exists(RECORDINGS_FOLDER):
        os.mkdir(RECORDINGS_FOLDER)
    if not os.path.exists(TODAY_FOLDER):
        os.mkdir(TODAY_FOLDER)

    # Get today's day
    now = datetime.datetime.now()
    nowDay = now.strftime("%Y-%m-%d")

    # Get all files inside TODAY_FOLDER
    logger.info("Get files inside TODAY_FOLDER")
    onlyFiles = filter(lambda x: os.path.isfile(os.path.join(TODAY_FOLDER, x)), os.listdir(TODAY_FOLDER))
    onlyFiles = [file for file in onlyFiles if file.endswith(".mp4") and nowDay not in file]
    onlyFiles = sorted(onlyFiles)

    # Iterate over every file
    for file in onlyFiles:
        logger.info("---")
        # Get datetime %Y-%m-%d_%H-%M-%S from FILE
        fileTimestamp = file.replace(".mp4", "")

        # Get day %Y-%m-%d
        day = datetime.datetime.strptime(fileTimestamp, "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d")

        # Check if dayFolder exists
        dayFolder = os.path.join(RECORDINGS_FOLDER, day)
        if not os.path.exists(dayFolder):
            os.mkdir(dayFolder)

        # Move file from today folder to dayFolder
        ogFullPath = os.path.join(TODAY_FOLDER, file)
        newFullPath = os.path.join(dayFolder, file)
        os.rename(ogFullPath, newFullPath)
        logger.info(ogFullPath)
        logger.info(newFullPath)

    # Check if Main script is running
    procs = [proc for proc in psutil.process_iter(attrs=["cmdline"]) if "RaspberryPiSurveillance.py" in '\t'.join(proc.info["cmdline"])]
    isRunning = True if len(procs) != 0 else False
    isTime = START_DATE <= now <= END_DATE

    if isTime and not isRunning:
        logger.info("isTime && NOT running -> RUN")
        runMain()
    elif not isTime and isRunning:
        logger.info("NOT isTime && isRunning - KILL")
        killMain(procs)
    else:
        logger.info("isRunning " + str(isRunning) + " | " + " isTime " + str(isTime))
        logger.info("nothing to do")


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
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
