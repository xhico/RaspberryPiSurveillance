# -*- coding: utf-8 -*-
# !/usr/bin/python3

import datetime
import json
import os
import traceback

import yagmail
import sys

import RaspberryPiSurveillance

EMAIL_USER = RaspberryPiSurveillance.EMAIL_USER
EMAIL_RECEIVER = RaspberryPiSurveillance.EMAIL_RECEIVER
EMAIL_APPPW = RaspberryPiSurveillance.EMAIL_APPPW


def main():
    # Get REC_FILE && Set MP4_File
    REC_FILE = sys.argv[1]
    print("REC_FILE:", REC_FILE)
    MP4_FILE = REC_FILE.replace(".h264", ".mp4")
    print("MP4_FILE:", MP4_FILE)
    REC_DATE = os.path.basename(MP4_FILE).replace(".mp4", "")

    # Convert H264 -> MP4
    print("MP4Box")
    cmd = " ".join(["MP4Box", "-quiet", "-add", REC_FILE, MP4_FILE])
    os.system(cmd)
    os.remove(REC_FILE)

    # Send email
    print("Send Email")
    subject = "EYE - " + REC_DATE
    # yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, subject, subject, MP4_FILE)
    yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, subject, subject)


if __name__ == '__main__':
    print("----------------------------------------------------")
    print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # Main
    try:
        main()
    except Exception as ex:
        print(traceback.format_exc())
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        print("End")
