# -*- coding: utf-8 -*-
# !/usr/bin/python3

# sudo apt-get install python3 python3-pip python3-dev python3-rpi.gpio libatlas-base-dev gpac libxslt-dev -y
# pip3 install yagmail picamera numpy

import os
import time
import signal
import subprocess
from dotenv import load_dotenv
load_dotenv()

debug = False
MAC_ADDR = os.environ.get('BLUETOOTH')


def scanXhico():
    if debug:
        print("Scanning for bluetooth")

    process = subprocess.Popen(['sudo', 'l2ping', '-c', '1', MAC_ADDR],
                               bufsize=1,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    while True:
        line = process.stdout.readlines()
        if not line:
            break
        else:
            if "Host is down" in str(line):
                return False
            else:
                return True

    return False


def stopRun():
    if debug:
        print("Stop")

    os.system('kill $(ps ax | grep \'python3 /home/pi/nsa/snowden.py\' | grep -v grep | awk \'{print $1}\')')

    global isRunning
    isRunning = False
    return


def startRun():
    if debug:
        print("Start")
    
    os.system("python3 /home/pi/nsa/snowden.py &")

    global isRunning
    isRunning = True
    return


if __name__ == '__main__':
    isRunning = False

    while True:
        isHere = scanXhico()

        if debug:
            print("isHere - " + str(isHere))
        if debug:
            print("isRunning - " + str(isRunning))

        if isHere and isRunning:
            stopRun()
        elif not isHere and not isRunning:
            startRun()

        if debug:
            print("")
        time.sleep(5)
