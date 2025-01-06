import pexpect
import logging
import os
import sys
import time
from power_commands import *
from led_commands import *

OLD_DEBUGGER = 0
NEW_DEBUGGER = 1

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def enable_RDP_debugger(tel):
    tel.sendline("stm32f1x lock 0")
    logging.info("Debugger RDP Enabled")
    return None

def get_flash_size(tel):
    tel.sendline("flash probe 0")  # Send command to get flash info

    # Wait for the response containing "flash size" or prompt timeout
    match = tel.expect(["flash size = 64 KiB", "flash size = 128 KiB" , "STM32 flash size failed", pexpect.TIMEOUT], timeout=5)
    
    if match == 0:  # Matched "flash size = 64 KiB"
        logging.info("Flash size detected: 64 KiB")
        return 64
    elif match == 1:  # Matched "flash size = 128 KiB"
        logging.info("Flash size detected: 128 KiB")
        return 128

def connect_telnet():
    tel = pexpect.spawn("telnet localhost 4444", timeout=10)

    telcon_start = tel.expect([
        "> ",
        "unable to"
    ])
    
    if telcon_start == 0:
        logging.info("Connected to telnet")
        return tel
    else:
        logging.error("Connection failed")
        
def halt(tel):
    tel.sendline("reset halt")
    # Expect the message and capture the dynamic CPU family
    match = tel.expect(r'\[(stm32[^\.]+(?:\.[^]]+)?)\] halted due to debug-request, current mode: Thread')

    # If the message is found, the CPU ID will be in the match group
    if match != -1:
        # Capture the dynamic CPU ID (family and the rest)
        cpu_id = tel.match.group(1)
        logging.info(f"Debugger halted the CPU with ID: {cpu_id} in Thread mode.")
        return True
    else:
        logging.info("Expected message not found. no CPU detected")
        return False

def reset(tel):
    tel.sendline("reset")
    logging.info("Chip reset")
    return True

def remove_protection(tel):
    tel.sendline("stm32f1x unlock 0")
    match = tel.expect("[\s\S]*unlocked[\s\S]*")
    if match != -1:
        logging.info("Protection removed")
        return True
    else:
        logging.info("Protection not removed")
        return False
    
def erase(tel):
    fail_count = 0
    tel.sendline("stm32f1x mass_erase 0")
    match = tel.expect(["stm32x mass erase complete", pexpect.TIMEOUT], timeout=1)
    if match == 0:
        logging.info("Flash erased")
        return True
    else:
        logging.info("Flash not erased")
        return False
         
def load_debugger_firmware(tel,version):
    if version == NEW_DEBUGGER:
        tel.sendline("flash write_image erase /home/ProvisioningJig/Desktop/ProvisioningJig_Code/f103cb_V2J45_full.hex")
        match = tel.expect(["[\s\S]*wrote[\s\S]*" , "stm32x device protected" , pexpect.TIMEOUT], timeout=5)
        if match == 0:
            tel.sendline("verify_image /home/ProvisioningJig/Desktop/ProvisioningJig_Code/f103cb_V2J45_full.hex")
            match = tel.expect("verified[\s\S]*bytes in")
            if match == 0:
                logging.info("New Debugger Flashed!")
                return True
        else:
            return False
    elif version == OLD_DEBUGGER:
        tel.sendline("flash write_image erase /home/ProvisioningJig/Desktop/ProvisioningJig_Code/f103c8_V2J45_normal.hex")
        match = tel.expect(["[\s\S]*wrote[\s\S]*" , "stm32x device protected" , pexpect.TIMEOUT], timeout=5)
        if match == 0:
            tel.sendline("verify_image /home/ProvisioningJig/Desktop/ProvisioningJig_Code/f103c8_V2J45_normal.hex")
            match = tel.expect("verified[\s\S]*bytes in")
            if match == 0:
                logging.info("Old Debugger Flashed!")
                return True
        else:
            return False

def load_target_firmware(tel):
    tel.sendline("flash write_image erase /home/ProvisioningJig/Desktop/ProvisioningJig_Code/target_firmware.elf")
    # tel.expect("wrote[\s\S]*from file")
    tel.sendline("verify_image /home/ProvisioningJig/Desktop/ProvisioningJig_Code/target_firmware.elf")
    # tel.expect("verified[\s\S]*bytes in")
    logger.info("Loaded Firmware on Target")

def terminate_telnet(tel):
    tel.sendline("exit")
    logging.info("Telnet connection terminated")
    tel.close()

def flash_debugger(version):
    tel = connect_telnet()
    if halt(tel):
        if remove_protection(tel):
            if not erase(tel):                 # previously programmed, trying again
                halt(tel)
                remove_protection(tel)
                erase(tel)
            if load_debugger_firmware(tel,version):
                enable_RDP_debugger(tel)
                reset(tel)
                terminate_telnet(tel)
                return True
            else:
                Debug_power(OFF)
                Debug_power(ON)
                flash_debugger(version)
    return False

def flash_target():
    tel = connect_telnet()
    target_LED(ON)
    if halt(tel):
        time.sleep(0.1)
        if erase(tel):
            time.sleep(0.1)
            if load_target_firmware(tel):
                time.sleep(0.1)
                terminate_telnet(tel)
                return True
    return False
