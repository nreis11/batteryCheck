import os
import re
import time
import sys

# Path where controller info exists
DEVICE_PATH = "/sys/class/power_supply"

# Get current directory. Icons and check log are stored relative to this python file
currentDirectory = os.path.dirname(os.path.realpath(sys.argv[0]))

dispExecPath = currentDirectory + "/code/batDisplay"
dispCmdOptions = "-x 24 -y 16 -t 5"  # Can change '-x 32 -y 32 -s 32 -t 3'

# Path for logging battery checks. Logging will be enabled if this file exists
batLog = currentDirectory + "/batteryCheckLog.temp"
batLogEnable = 0

# Path for battery icons (including the 'bat' part of batX.png file name for convenience)
iconPath = currentDirectory + "/icons/bat"

# Debugging enable/disable
__debug = False

# Connected devices
knownDevices = {
    # "00214130952" : 3
}


def callDisplayFunc(batVal):
    """Use to call the battery display func."""
    dispCmd = (
        dispExecPath + " " + dispCmdOptions + " " + iconPath + str(batVal) + ".png"
    )
    if __debug:
        print("calling display function: " + dispCmd)
    else:
        os.system(dispCmd)


def formatKey(deviceId):
    """Use MAC address as ID. Capture numbers."""
    numbers = re.findall("[0-9]+", deviceId)
    return "".join(numbers)


def getCurrDevices(devicePath):
    """Returns list of all sony controllers."""
    return [d for d in os.listdir(devicePath) if "sony" in d.lower()]


def getIdAndVal(device):
    batteryFile = f"{DEVICE_PATH}/{device}/capacity"
    with open(batteryFile) as bf:
        # (25,50,75,100)
        batStr = bf.readline().strip()
        batVal = int(batStr) // 25 if batStr.isdigit() else 0
        deviceId = formatKey(device)
        return (deviceId, batVal)


def main():
    """Watches for changes in device path and runs functions depeneding on change."""
    if not os.path.exists(DEVICE_PATH):
        raise FileNotFoundError(f"Device directory {DEVICE_PATH} not found. Halting.")

    while True:
        currDevices = getCurrDevices(DEVICE_PATH)
        if __debug:
            print(f"\nBEFORE: KNOWN DEVICES: {knownDevices}")

        if len(currDevices) > len(knownDevices):
            # Detected new controller
            for d in currDevices:
                deviceId, batVal = getIdAndVal(d)
                if deviceId not in knownDevices:
                    knownDevices[deviceId] = batVal
                    callDisplayFunc(batVal)
        elif len(currDevices) < len(knownDevices):
            # Controller disconnected
            knownDevices.clear()
            for d in currDevices:
                deviceId, batVal = getIdAndVal(d)
                knownDevices[deviceId] = batVal

        if __debug:
            print(f"AFTER: KNOWN DEVICES: {knownDevices}")
            break

        time.sleep(2)


if __name__ == "__main__":
    main()
else:
    __debug = True
