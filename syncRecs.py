# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import datetime
import traceback

import psutil
import yagmail

import RaspberryPiSurveillance

EMAIL_USER = RaspberryPiSurveillance.EMAIL_USER
EMAIL_RECEIVER = RaspberryPiSurveillance.EMAIL_RECEIVER
EMAIL_APPPW = RaspberryPiSurveillance.EMAIL_APPPW
START_DATE = RaspberryPiSurveillance.START_DATE
END_DATE = RaspberryPiSurveillance.END_DATE
writeLog = RaspberryPiSurveillance.writeLog
RECORDINGS_FOLDER = RaspberryPiSurveillance.RECORDINGS_FOLDER
TODAY_FOLDER = RaspberryPiSurveillance.TODAY_FOLDER
SCRIPT_FOLDER = RaspberryPiSurveillance.SCRIPT_FOLDER


def main():
    # Check if FOLDERS exist
    print("Check RECORDINGS_FOLDER && TODAY_FOLDER")
    if not os.path.exists(RECORDINGS_FOLDER):
        os.mkdir(RECORDINGS_FOLDER)
    if not os.path.exists(TODAY_FOLDER):
        os.mkdir(TODAY_FOLDER)

    # Get today's day
    now = datetime.datetime.now()
    nowDay = now.strftime("%Y-%m-%d")

    # Get all files inside TODAY_FOLDER
    print("Get files inside TODAY_FOLDER")
    onlyFiles = filter(lambda x: os.path.isfile(os.path.join(TODAY_FOLDER, x)), os.listdir(TODAY_FOLDER))
    onlyFiles = [file for file in onlyFiles if file.endswith(".mp4") and nowDay not in file]
    onlyFiles = sorted(onlyFiles)

    # Iterate over every file
    for file in onlyFiles:
        print("---")
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
        print(ogFullPath)
        print(newFullPath)

    # Check if Main script is running
    procs = [proc for proc in psutil.process_iter(attrs=["cmdline"]) if "RaspberryPiSurveillance.py" in '\t'.join(proc.info["cmdline"])]
    if len(procs) == 0 and START_DATE <= now <= END_DATE:
        print("NOT RUNNING && SHOULD BE -> RUN")
        cmd = " ".join(["python3", os.path.join(SCRIPT_FOLDER, "RaspberryPiSurveillance.py"), ">", "/dev/null", "&"])
        os.system(cmd)
    elif len(procs) == 0 and not START_DATE <= now <= END_DATE:
        print("NOT RUNNING && SHOULDN'T BE -> NOTHING")
    elif len(procs) != 0 and START_DATE <= now <= END_DATE:
        print("RUNNING && SHOULD BE -> CONTINUE")
    elif len(procs) != 0 and not START_DATE <= now <= END_DATE:
        print("RUNNING && SHOULDN'T BE -> KILL")
        for proc in procs:
            print(proc.kill())
        writeLog(now.strftime("%Y/%m/%d %H:%M:%S"))
        writeLog("Stopped")
        writeLog("----------------------------------------------------\n")
    else:
        print("ELSE")


if __name__ == '__main__':
    print("----------------------------------------------------")
    print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # Main
    try:
        main()
    except Exception as ex:
        print(traceback.format_exc())
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
