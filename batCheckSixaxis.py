#!/usr/bin/env python3
import os
import sys
import logging
from inotify_simple import INotify, flags


# Path where controller info exists
DEVICE_PATH = "/sys/class/power_supply"

# Time in seconds between device checks
# TIMEOUT_INTERVAL = 2
# Toggle battery info logging
BAT_LOG_ENABLE = 0

# Get current directory. Icons and check log are stored relative to this python file
curr_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

if BAT_LOG_ENABLE:
    logging.basicConfig(
        filename=os.path.join(curr_dir, "batteryCheckLog.temp"),
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )

disp_exec_path = os.path.join(curr_dir, "code/batDisplay")
disp_cmd_options = "-x 24 -y 16 -t 5"  # Can change '-x 32 -y 32 -s 32 -t 3'

# Path for battery icons
icon_path = os.path.join(curr_dir, "icons")

# Debugging enable/disable
__debug = False


def call_display_func(bat_val: int) -> None:
    """Calls the battery display function with a constructed command."""
    icon_file = os.path.join(icon_path, f"bat{bat_val}.png")
    disp_cmd = f"{disp_exec_path} {disp_cmd_options} {icon_file}"
    if __debug:
        print(f"Calling display function: {disp_cmd}")
    else:
        os.system(disp_cmd)


def get_bat_val(device: str) -> int:
    """Reads and returns battery value as an integer."""
    try:
        with open(os.path.join(DEVICE_PATH, device, "capacity")) as bf:
            return int(bf.readline().strip()) // 25
    except (ValueError, FileNotFoundError):
        return 0


def main() -> None:
    """Monitors the power supply directory for changes."""
    if not os.path.exists(DEVICE_PATH):
        raise FileNotFoundError(f"Device directory {DEVICE_PATH} not found. Halting.")
    connected_devices = {
        # <device>: <bat_val>
        # "sony_controller_battery_00:21:4f:13:09:52" : 3
    }
    # Set up inotify to monitor the device path for changes
    inotify = INotify()
    watch_flags = flags.CREATE | flags.DELETE
    inotify.add_watch(DEVICE_PATH, watch_flags)

    print("Monitoring for new devices...")

    while True:
        for event in inotify.read():  # Block until an event occurs
            for flag in flags.from_mask(event.mask):
                device = event.name  # Get the file or directory name
                if "sony" in device.lower():
                    if flag == flags.CREATE and device not in connected_devices:
                        # A new device was added
                        bat_val = get_bat_val(device)
                        connected_devices[device] = bat_val
                        call_display_func(bat_val)
                        if BAT_LOG_ENABLE:
                            logging.info(
                                f"Detected new device: {device} with battery {bat_val}"
                            )
                    elif flag == flags.DELETE and device in connected_devices:
                        # A device was removed
                        del connected_devices[device]
                        if BAT_LOG_ENABLE:
                            logging.info(f"Removed device: {device}")


if __name__ == "__main__":
    if os.name != "posix":
        raise EnvironmentError("This script can only run on Linux.")
    try:
        main()
    except KeyboardInterrupt:
        print("Terminating script...")
        sys.exit(0)
else:
    __debug = True
