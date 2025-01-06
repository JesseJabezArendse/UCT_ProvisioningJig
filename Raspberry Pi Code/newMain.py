

from openOCD_commands import start_openOCD_for_debugger, start_openOCD_for_target
from telnet_commands import *
from upgrade_stlink import *
from power_commands import *
from led_commands import *
import time

print("Hello from UCT EEE ProvisioningJig v3! - STLink version V2J45")
print("Author: Jesse Jabez Arendse")
print("Date Modified: 18/12/2024")
print("python script: /home/ProvisioningJig/Desktop/ProvisioningJig_Code/newMain.py")
print("username and pwd are ProvisioningJig")

# detection pins
DEBUG_DET = 5
TARGET_DET = 13

areLEDsON = False
new_stlink = 0

def check_if_new_debugger():
    time.sleep(4)
    target_model = "sda"
    try:
        # Spawn a shell process
        lsblk = pexpect.spawn("lsblk -o NAME", encoding="utf-8")
        
        # Send the lsblk command
        lsblk.sendline("lsblk -o NAME")
        
        # Wait for the command to complete
        lsblk.expect(pexpect.EOF)
        
        # Get the full output of the command
        output = lsblk.before
        
        # Count occurrences of the target model
        count = 0
        for line in output.splitlines():
            if target_model.lower() in line.lower():  # Case-insensitive check
                count += 1
        
        # Return True if there are 2 or more instances
        return count
    except pexpect.ExceptionPexpect as e:
        print(f"Error running lsblk: {e}")
        return False

def debug_detected():
    all_off()
    logging.info(f"Debugger Detected!")
    time.sleep(2)
    debug_LED(ON)
    time.sleep(2)
    provision_debugger()
    return None

def target_detected():
    all_off()
    logging.info(f"Target Detected!")
    time.sleep(2)
    target_LED(ON)
    time.sleep(2)
    provision_target()
    return None

def setup_Detections():
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    GPIO.setup(DEBUG_DET,  GPIO.IN)
    GPIO.setup(TARGET_DET, GPIO.IN)
    return None

def provision_debugger():
    try:
        all_off()
        STLink_power(ON)
        debug_LED(ON)
        Debug_power(ON)

        with start_openOCD_for_debugger() as OCD_success:
            if OCD_success:
                flash_debugger(NEW_DEBUGGER)
            else:
                all_off()
        Debug_power(OFF)
        STLink_power(OFF)
        time.sleep(0.2)
        Debug_power(ON)
        STLink_power(ON)
        curr_num_debuggers = check_if_new_debugger()
        if curr_num_debuggers != new_stlink + 1:
            logging.info(f"Debugger is actually old")
            with start_openOCD_for_debugger() as OCD_success:
                if OCD_success:
                    flash_debugger(OLD_DEBUGGER)
                else:
                    all_off()
        all_off()
        done_LED(ON)

    except TypeError as e:
        print(f"An error occurred: {e}")
        all_off()  # Ensure everything is turned off on error

    finally:
        print("Provisioning complete.")

    return None
    
def provision_target():
    try:
        all_off()
        STLink_power(ON)
        Target_power(ON)

        with start_openOCD_for_target() as OCD_success:
            if OCD_success:
                target_LED(ON)
                flash_target()
                all_off()
                done_LED(ON)
            else:
                all_off()
        time.sleep(8)

    except TypeError as e:
        print(f"An error occurred: {e}")
        all_off()  # Ensure everything is turned off on error

    finally:
        pass
        print("Provisioning complete.")

    return None

def all_off():
    LEDs(OFF)
    STLink_power(ON)
    Target_power(OFF)
    Debug_power(OFF)
    return None

def check_pins():
    debug_state = GPIO.input(DEBUG_DET)  # Read DEBUG_DET pin
    target_state = GPIO.input(TARGET_DET)  # Read TARGET_DET pin
    print(f"DEBUG_DET: {'HIGH' if debug_state else 'LOW'}, TARGET_DET: {'HIGH' if target_state else 'LOW'}")
    return [debug_state , target_state]

def idleIndicate():
    global areLEDsON
    if areLEDsON:
        LEDs(OFF)
        areLEDsON = False
    else:
        LEDs(ON)
        areLEDsON = True
    return None

def main():
    setup_Detections()

    while True:
        all_off()
        time.sleep(0.5)  # Poll every 0.5 seconds
        [debug_state,target_state] = check_pins()
        if debug_state:
            debug_detected() # do the things
            while debug_state: 
                [debug_state,target_state] = check_pins() # wait until debugger is disconnected
                time.sleep(0.2)
            time.sleep(1)
            all_off()
        elif target_state:
            target_detected() # do the things
            while target_state: 
                [debug_state,target_state] = check_pins() # wait until debugger is disconnected
                time.sleep(0.2)
            time.sleep(1)
            all_off()
        else:
            provision_target() # polls cause target detection doesnt work

        idleIndicate()
    return None

if __name__ == "__main__":
    all_off()
    STLink_power(ON)
    new_stlink = check_if_new_debugger()
    if new_stlink == 1:
        logging.info(f"STLink = New Debugger plugged")
    if new_stlink == 0:
        logging.info(f"STLink = Old Debugger plugged")
    main()
    



