#!/usr/bin/env python3
import os
import time
import sys
from inotify_simple import INotify, flags


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


def get_curr_devices(device_path: str) -> list[str]:
    """Returns list of all sony controllers."""
    return [d for d in os.listdir(device_path) if "sony" in d.lower()]


def call_display_func(bat_val: int) -> None:
    """Calls the battery display function with a constructed command."""
    icon_file = os.path.join(icon_path, f"{bat_val}.png")
    disp_cmd = f"{disp_exec_path} {disp_cmd_options} {icon_file}"
    if __debug:
        print(f"Calling display function: {disp_cmd}")
    else:
        os.system(disp_cmd)


def get_battery_val(device: str) -> int:
    try:
        with open(os.path.join(DEVICE_PATH, device, "capacity")) as bf:
            # Enumerated values should be 25, 50, 75, 100
            return int(bf.readline().strip()) // 25
    except (ValueError, FileNotFoundError):
        return 0


def main() -> None:
    """Monitors the power supply directory for changes."""
    if not os.path.exists(DEVICE_PATH):
        raise FileNotFoundError(f"Device directory {DEVICE_PATH} not found. Halting.")
    connected_devices = {
        # [device]: [bat_val]
        # "sony_controller_battery_00:21:4f:13:09:52" : 3
    }
    # Set up inotify to monitor the device path for changes
    inotify = INotify()
    watch_flags = flags.CREATE | flags.DELETE
    wd = inotify.add_watch(DEVICE_PATH, watch_flags)

    print("Monitoring for new devices...")

    while True:
        for event in inotify.read():  # Block until an event occurs
            for flag in flags.from_mask(event.mask):
                device = event.name  # Get the file or directory name
                if "sony" in device.lower():
                    if flag == flags.CREATE and device not in connected_devices:
                        # A new device was added
                        bat_val = get_battery_val(device)
                        connected_devices[device] = bat_val
                        print(
                            f"New device detected: {device}, battery level: {bat_val}"
                        )
                        call_display_func(bat_val)
                    elif flag == flags.DELETE and device in connected_devices:
                        # A device was removed
                        print(f"Device removed: {device}")
                        del connected_devices[device]

        # Sleep as a fallback in case no events are detected
        time.sleep(TIMEOUT_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Terminating script...")
        sys.exit(0)
else:
    __debug = True
