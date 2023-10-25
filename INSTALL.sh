#!/bin/bash

sudo mv /home/pi/RaspberryPiSurveillance/RaspberryPiSurveillance.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install yagmail moviepy gpiozero picamera2 --no-cache-dir
sudo apt install python3-numpy python3-kms++ python3-libcamera -y
mkdir -p /home/pi/RaspberryPiSurveillance/_RECORDINGS
chmod +x -R /home/pi/RaspberryPiSurveillance/*