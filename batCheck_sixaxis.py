import os
import re
import time
import sys

DEVICE_PATH = "/sys/class/power_supply"

dispExecPath = "~/customscripts/batteryCheck/code/batDisplay"
dispCmdOptions = "-x 24 -y 16 -t 5"  # Can change '-x 32 -y 32 -s 32 -t 3'

# Get current directory. Icons and check log are stored relative to this python file
currentDirectory = os.path.dirname(os.path.realpath(sys.argv[0]))

# Path for logging battery checks. Logging will be enable if this file exists
batLog = currentDirectory + "/batteryCheckLog.temp"
batLogEnable = 0

# Path for battery icons (including the 'bat' part of bat_.png file name for convenience)
iconPath = currentDirectory + "/icons/bat"

# Debugging enable/disable
__debug = False


def callDisplayFunc(batVal):
    dispCmd = (
        dispExecPath + " " + dispCmdOptions + " " + iconPath + str(batVal) + ".png"
    )
    if __debug:
        print("calling display function: " + dispCmd)
    else:
        os.system(dispCmd)


def formatKey(deviceId):
    numbers = re.findall("[0-9]+", deviceId)
    return "".join(numbers)


def getCurrDevices(devicePath):
    """Returns list of all sony controllers."""
    return [d for d in os.listdir(devicePath) if "sony" in d.lower()]


def getIdAndVal(device):
    batteryFile = f"{DEVICE_PATH}/{device}/capacity"
    with open(batteryFile) as bf:
        # (25,50,75,100)
        batStr = bf.readline()
        batVal = int(int(batStr) * 0.04) if batStr.isdigit() else 0
        deviceId = formatKey(device)
        return (deviceId, batVal)


knownDevices = {
    # "00214130952" : 3
}
# Init dict with device id as key, value as battery
# Compare len of dict with len of deviceDir
# If curr len > len dict, iterate through dir, if device not in dict, add and displayBat exec


def main():
    currDevices = getCurrDevices(DEVICE_PATH)
    if __debug:
        print("BEFORE:")
        print(f"KNOWN DEVICES: {knownDevices}")

    if len(currDevices) > len(knownDevices):
        # Detected new controller
        for d in currDevices:
            deviceId, batVal = getIdAndVal(d)
            if deviceId not in knownDevices:
                knownDevices[deviceId] = batVal
                callDisplayFunc(batVal)
    # Or curr len < len dict, recreate device dict
    elif len(currDevices) < len(knownDevices):
        # Controller disconnected
        knownDevices.clear()
        for d in currDevices:
            deviceId, batVal = getIdAndVal(d)
            knownDevices[deviceId] = batVal

    if __debug:
        print("AFTER")
        print(f"KNOWN DEVICES: {knownDevices}")

    # time.sleep(2)


if __name__ == "__main__":
    main()
else:
    __debug = True
    DEVICE_PATH = "./tmp"