# -*- coding: utf-8 -*-
# !/usr/bin/python3


import io
import os
import time
import glob
import yagmail
import picamera
import picamera.array
import numpy as np
from threading import Thread
import subprocess
from nsa import debug
from dotenv import load_dotenv
load_dotenv()


REC_WIDTH = 640              # video width
REC_HEIGHT = 480             # video height
REC_FRAMERATE = 24           # the recording framerate
REC_SECONDS = 10             # number of seconds before and after motion
REC_BITRATE = 500000         # bitrate for H.264 encoder
REC_ROTATION = 180           # rotation
FILE_BUFFER = 548576         # the size of the file buffer (bytes)

MOTION_MAGNITUDE = 65        # the magnitude of vectors required for motion
MOTION_VECTORS = 5           # the number of vectors required to detect motion

EMAIL_SENDER = os.environ.get('MAIL_USER')          # email account that sends the email
EMAIL_PASSWORD = os.environ.get('MAIL_PASS')        # password for the email sender account
EMAIL_RECEIVER = os.environ.get('MAIL_RECEIVER')    # email to send the video


class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, size=None):
        super(MotionDetector, self).__init__(camera, size)
        self.vector_count = 0
        self.detected = 0

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        vector_count = (a > MOTION_MAGNITUDE).sum()

        if vector_count > MOTION_VECTORS:
            self.detected = time.time()
            self.vector_count = vector_count


def write_video(stream):
    with io.open('before.h264', 'wb') as output:
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    stream.seek(0)
    stream.truncate()


def send_mail(fileVid):
    if debug:
        print("Send Email")

    yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)

    if round(os.path.getsize(fileVid) / 1024) > 20000:
        os.system("MP4Box -splits 20000 " + fileVid + " > /dev/null 2>&1")
        getFiles = glob.glob(fileVid.split("//")[1].split(".mp4")[0] + '*.mp4')

        for file in getFiles:
            yag.send(EMAIL_RECEIVER, "NSA - " + file, "", file)
            os.remove(file)
    else:
        yag.send(EMAIL_RECEIVER, "NSA - " + fileVid, "", fileVid)

    yag.close()

    if debug:
        print("Email Sent")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with picamera.PiCamera() as camera:
        camera.resolution = (REC_WIDTH, REC_HEIGHT)
        camera.framerate = REC_FRAMERATE
        camera.rotation = REC_ROTATION

        time.sleep(2)

        motion_detector = MotionDetector(camera)
        stream = picamera.PiCameraCircularIO(camera, size=FILE_BUFFER)
        camera.start_recording(stream, format='h264', bitrate=REC_BITRATE,
                               intra_period=REC_FRAMERATE, motion_output=motion_detector)

        try:
            while True:
                if debug:
                    print('Waiting for motion')
                while motion_detector.detected < time.time() - 1:
                    camera.wait_recording(1)

                motionTime = str(time.strftime('%Y-%m-%d_%H-%M-%S'))
                if debug:
                    print('Motion detected (' + str(motion_detector.vector_count) + ' vectors) ' + motionTime)
                camera.split_recording('after.h264')
                write_video(stream)

                while motion_detector.detected > time.time() - REC_SECONDS:
                    camera.wait_recording(1)

                if debug:
                    print('Motion stopped!')
                camera.split_recording(stream)

                videoPath = 'records/' + motionTime + '.mp4'
                os.system('MP4Box -add before.h264 -cat after.h264 ' + videoPath + ' > /dev/null 2>&1')
                os.system("rm -rf *.h264 *.h264")

                process = Thread(target=send_mail, args=[videoPath])
                process.start()

        finally:
            camera.stop_recording()


if __name__ == '__main__':
    main()
