import json
import usb.core
import usb.util
import time
import sys

def progress_bar(current, total, bar_length=40):
    fraction = current / total
    arrow = '█' * int(fraction * bar_length)
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f'\rProgress: |{arrow}{spaces}| {int(fraction * 100)}%')
    sys.stdout.flush()


# Function to send data
def send_data(dev, capdata_bytes):
    try:
        dev.write(0x02, capdata_bytes, timeout=1000)
        # print(f"Sent capdata: {capdata_bytes}")
    except usb.core.USBError as e:
        print(f"Failed to send packet: {e}")
        exit()

# Function to receive data
def receive_data(dev):
    try:
        received_data = dev.read(0x81, 64, timeout=1000)
        # print(f"Received raw data: {received_data}")
        return received_data
    except usb.core.USBError as e:
        print(f"Failed to receive data: {e}")
        exit()
        return None

def makeUpgradeable():
    print("Making ST-Link Upgradable, please wait")

    # Find your USB device
    dev = usb.core.find(idVendor=0x0483, idProduct=0x3748)
    if dev is None:
        raise ValueError("Device not found")

    dev.set_configuration()

    # Load your JSON file
    with open('upgrade_std_old_again.json', 'r') as f:
        datas = json.load(f)

    # Track the previous packet time
    previous_time = None

    # Process each packet
    index = 0
    for data in datas:
        index = index + 1
        progress_bar(index, len(datas))
        current_time = float(data["_source"]["layers"]["frame"]["frame.time_epoch"])

        if previous_time:
            # Calculate the time delay and wait
            time_delta = current_time - previous_time
            time.sleep(time_delta)
        previous_time = current_time

        usb_layer = data["_source"]["layers"]["usb"]
        
        # Check transfer type
        transfer_type = usb_layer.get("usb.transfer_type", "0x03")
        
        # Check if 'usb.capdata' key exists
        if "usb.capdata" in data["_source"]["layers"]:
            capdata_hex = data["_source"]["layers"]["usb.capdata"]
            capdata_bytes = bytes.fromhex(capdata_hex.replace(":", ""))
            
            # Check direction and transfer type
            direction = int(usb_layer["usb.irp_info_tree"]["usb.irp_info.direction"], 16)
            if direction == 0 and transfer_type == "0x03":
                # Out data - send data to device
                send_data(dev, capdata_bytes)
            elif direction == 1 and transfer_type == "0x03":
                # In data - receive data from device
                receive_data(dev)
            else:
                print(f"Skipping packet with unknown type: {transfer_type}")
        else:
            pass
            # print("No 'usb.capdata' key found, skipping entry.")

    return None

def upgradeToNew():
    print("Upgrading ST-Link to V2J45S0, please wait again")

    # Find your USB device
    dev = usb.core.find(idVendor=0x0483, idProduct=0x3748)
    if dev is None:
        raise ValueError("Device not found")

    dev.set_configuration()

    # Load your JSON file
    with open('upgrade_std_new_again.json', 'r') as f:
        datas = json.load(f)

    # Track the previous packet time
    previous_time = None

    # Process each packet
    index = 0
    for data in datas:
        index = index + 1
        progress_bar(index, len(datas))
        current_time = float(data["_source"]["layers"]["frame"]["frame.time_epoch"])

        if previous_time:
            # Calculate the time delay and wait
            time_delta = current_time - previous_time
            time.sleep(time_delta)
        previous_time = current_time

        usb_layer = data["_source"]["layers"]["usb"]
        
        # Check transfer type
        transfer_type = usb_layer.get("usb.transfer_type", "0x03")
        
        # Check if 'usb.capdata' key exists
        if "usb.capdata" in data["_source"]["layers"]:
            capdata_hex = data["_source"]["layers"]["usb.capdata"]
            capdata_bytes = bytes.fromhex(capdata_hex.replace(":", ""))
            
            # Check direction and transfer type
            direction = int(usb_layer["usb.irp_info_tree"]["usb.irp_info.direction"], 16)
            if direction == 0 and transfer_type == "0x03":
                # Out data - send data to device
                send_data(dev, capdata_bytes)
            elif direction == 1 and transfer_type == "0x03":
                # In data - receive data from device
                receive_data(dev)
            else:
                print(f"Skipping packet with unknown type: {transfer_type}")
        else:
            pass
            # print("No 'usb.capdata' key found, skipping entry.")



if __name__ == "__main__":
    makeUpgradeable()