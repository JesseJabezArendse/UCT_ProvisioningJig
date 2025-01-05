import RPi.GPIO as GPIO
import logging

# Pin definitions
DEBUG_LED = 2
TARGET_LED = 3
DONE_LED = 4

ON = True
OFF = False

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DEBUG_LED, GPIO.OUT)
GPIO.setup(TARGET_LED, GPIO.OUT)
GPIO.setup(DONE_LED, GPIO.OUT)

# Control the power for the ST-Link
def debug_LED(state):
    GPIO.output(DEBUG_LED, GPIO.HIGH if state else GPIO.LOW)
    # logging.info(f"Debug LED {'ON' if state else 'OFF'}")

def target_LED(state):
    GPIO.output(TARGET_LED, GPIO.HIGH if state else GPIO.LOW)
    # logging.info(f"Target LED {'ON' if state else 'OFF'}")

def done_LED(state):
    GPIO.output(DONE_LED, GPIO.HIGH if state else GPIO.LOW)
    # logging.info(f"Done LED {'ON' if state else 'OFF'}")

def LEDs(state):
    debug_LED (state)
    target_LED(state)
    done_LED  (state)



