# -*- coding: utf-8 -*-
# !/usr/bin/python3

from snowden import REC_WIDTH, REC_HEIGHT, REC_ROTATION, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from nsa import debug
from picamera import PiCamera
import yagmail
import time
import os


def send_mail(pic):
    yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
    yag.send(EMAIL_RECEIVER, "NSA - " + pic, "", pic)
    yag.close()


def takePic(file):
    camera = PiCamera()
    camera.resolution = (REC_WIDTH, REC_HEIGHT)
    camera.rotation = REC_ROTATION
    camera.start_preview()
    time.sleep(5)
    camera.capture(file)
    camera.stop_preview()
    camera.close()


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if debug:
        print("Kill nsa")
    os.system('kill $(ps ax | grep \'python3 /home/pi/nsa/nsa.py\' | grep -v grep | awk \'{print $1}\')')
    os.system('kill $(ps ax | grep \'python3 /home/pi/nsa/snowden.py\' | grep -v grep | awk \'{print $1}\')')

    picFile = "pic_" + str(time.strftime('%Y-%m-%d_%H-%M-%S')) + ".jpg"

    if debug:
        print("TakePic")
    takePic(picFile)
    if debug:
        print("SendMail")
    send_mail(picFile)
    if debug:
        print("RemovePic")
    os.remove(picFile)

    if debug:
        print("Start nsa")
    os.system("python3 /home/pi/nsa/nsa.py &")


if __name__ == '__main__':
    main()
