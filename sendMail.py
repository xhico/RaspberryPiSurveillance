# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import traceback
import yagmail
import sys
import logging
import RaspberryPiSurveillance


def main():
    # Get REC_FILE && Set REC_DATE
    REC_FILE = sys.argv[1]
    REC_DATE = os.path.basename(REC_FILE).replace(".mp4", "")
    logger.info("REC_DATE: " + REC_DATE)

    # Send email
    logger.info("Send Email")
    subject = "EYE - " + REC_DATE
    yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, subject, subject)


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    EMAIL_USER = RaspberryPiSurveillance.EMAIL_USER
    EMAIL_RECEIVER = RaspberryPiSurveillance.EMAIL_RECEIVER
    EMAIL_APPPW = RaspberryPiSurveillance.EMAIL_APPPW

    # Main
    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
