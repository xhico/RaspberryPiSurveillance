#!/bin/bash

sudo mv /home/pi/RaspberryPiSurveillance/RaspberryPiSurveillance.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install yagmail moviepy gpiozero picamera2 --no-cache-dir
mkdir -p /home/pi/RaspberryPiSurveillance/_RECORDINGS
chmod +x -R /home/pi/RaspberryPiSurveillance/*