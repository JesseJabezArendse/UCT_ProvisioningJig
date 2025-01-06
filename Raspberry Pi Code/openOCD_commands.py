import pexpect
import logging
import os
import sys

openOCD_executable = "openOCD/bin/openocd.exe"  # Path to openOCD executable
openOCD_command = "openocd"

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Verify that the openOCD executable exists
# if not os.path.isfile(openOCD_executable):
#     logger.critical(f"{openOCD_executable} not found. Please check the path.")
#     sys.exit(1)

def start_openOCD_for_debugger():
    # Spawn OpenOCD process with pexpect
    try:
        ocd = pexpect.spawn( f'{openOCD_command} -f interface/stlink.cfg -f target/stm32f1x.cfg -c "transport select hla_swd" -c "adapter speed 4000" ', timeout=None)
        logger.info("OpenOCD process started")

        # Check for success or error messages
        openocd_start_state = ocd.expect([
            r"Listening on port 3333 for gdb connections",  # Success pattern
            r"Error: open failed",  # Common error patterns
            r"Error: couldn't bind to socket: Address already in use",
            r"init mode failed \(unable to connect to the target\)"
        ])

        if openocd_start_state == 0:
            logger.info("OpenOCD started successfully and is ready for gdb connections")
            return ocd
        elif openocd_start_state == 1:
            logger.critical("OpenOCD failed to open")
            return False
        elif openocd_start_state == 2:
            logger.critical("OpenOCD is already active, please close other instances and retry")
            return False
        else:
            logger.critical("Failed to initialize OpenOCD: Unable to connect to the target")
            return False

    except pexpect.TIMEOUT:
        logger.error("Timeout: OpenOCD did not start successfully within the expected time frame.")
        return False

def start_openOCD_for_target():
    # Spawn OpenOCD process with pexpect
    try:
        ocd = pexpect.spawn(f'{openOCD_command} -f interface/stlink.cfg -f target/stm32f0x.cfg -c "transport select hla_swd"', timeout=None)
        logger.info("OpenOCD process started")

        # Check for success or error messages
        openocd_start_state = ocd.expect([
            r"Listening on port 3333 for gdb connections",  # Success pattern
            r"Error: open failed",  # Common error patterns
            r"Error: couldn't bind to socket: Address already in use",
            r"init mode failed \(unable to connect to the target\)"
        ])

        if openocd_start_state == 0:
            logger.info("OpenOCD started successfully and is ready for gdb connections")
            return ocd
        elif openocd_start_state == 1:
            logger.critical("OpenOCD failed to open")
            return False
        elif openocd_start_state == 2:
            logger.critical("OpenOCD is already active, please close other instances and retry")
            return False
        else:
            logger.critical("Failed to initialize OpenOCD: Unable to connect to the target")
            return False

    except pexpect.TIMEOUT:
        logger.error("Timeout: OpenOCD did not start successfully within the expected time frame.")
        return False