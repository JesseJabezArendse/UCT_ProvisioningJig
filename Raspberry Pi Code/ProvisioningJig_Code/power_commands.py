import RPi.GPIO as GPIO
import logging

# Pin definitions
STLINK_PIN = 26
TARGET_PIN = 16
DEBUG_PIN = 27

ON = True
OFF = False

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STLINK_PIN, GPIO.OUT)
GPIO.setup(TARGET_PIN, GPIO.OUT)
GPIO.setup(DEBUG_PIN, GPIO.OUT)

# Control the power for the ST-Link
def STLink_power(state):
    GPIO.output(STLINK_PIN, GPIO.HIGH if state else GPIO.LOW)
    logging.info(f"ST-Link power {'ON' if state else 'OFF'}")

# Control the power for the Target
def Target_power(state):
    GPIO.output(TARGET_PIN, GPIO.HIGH if state else GPIO.LOW)
    logging.info(f"Target power {'ON' if state else 'OFF'}")

# Control the power for the Debugger
def Debug_power(state):
    GPIO.output(DEBUG_PIN, GPIO.HIGH if state else GPIO.LOW)
    logging.info(f"Debug power {'ON' if state else 'OFF'}")
