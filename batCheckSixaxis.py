#!/usr/bin/env python3
import os
import time
import sys

# Path where controller info exists
DEVICE_PATH = "/sys/class/power_supply"

# Time in seconds between device checks
TIMEOUT_INTERVAL = 2

# Get current directory. Icons and check log are stored relative to this python file
curr_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

disp_exec_path = curr_dir + "/code/batDisplay"
disp_cmd_options = "-x 24 -y 16 -t 5"  # Can change '-x 32 -y 32 -s 32 -t 3'

# Path for logging battery checks. Logging will be enabled if this file exists
bat_log = curr_dir + "/batteryCheckLog.temp"
bat_log_enable = 0

# Path for battery icons (including the 'bat' part of batX.png file name for convenience)
icon_path = curr_dir + "/icons/bat"

# Debugging enable/disable
__debug = False

# Connected devices
known_devices = {
    # [device]: [bat_val]
    # "sony_controller_battery_00:21:4f:13:09:52" : 3
}


def get_curr_devices(device_path: str) -> list[str]:
    """Returns list of all sony controllers."""
    return [d for d in os.listdir(device_path) if "sony" in d.lower()]


def call_display_func(bat_val: int) -> None:
    """Use to call the battery display func."""
    disp_cmd = f"{disp_exec_path} {disp_cmd_options} {icon_path + str(bat_val)}.png"
    if __debug:
        print("calling display function: " + disp_cmd)
    else:
        os.system(disp_cmd)


def get_bat_val(device: str) -> int:
    battery_file = f"{DEVICE_PATH}/{device}/capacity"
    with open(battery_file) as bf:
        # (25,50,75,100)
        bat_str = bf.readline().strip()
        bat_val = int(bat_str) // 25 if bat_str.isdigit() else 0
        return bat_val


def main() -> None:
    """Watches for new devices in device path and runs display func if new device is found"""
    if not os.path.exists(DEVICE_PATH):
        raise FileNotFoundError(f"Device directory {DEVICE_PATH} not found. Halting.")

    while True:
        if __debug:
            print(f"\nBEFORE: KNOWN DEVICES: {known_devices}")

        curr_devices = get_curr_devices(DEVICE_PATH)
        for device in curr_devices:
            # Only display battery info if new device is detected
            if device not in known_devices:
                bat_val = get_bat_val(device)
                known_devices[device] = bat_val
                call_display_func(bat_val)

        if __debug:
            print(f"AFTER: KNOWN DEVICES: {known_devices}")
            break

        time.sleep(TIMEOUT_INTERVAL)


if __name__ == "__main__":
    main()
else:
    __debug = True
