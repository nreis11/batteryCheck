# RetroPie PS3 Battery Indicator

Modified copy of files from the raspidmx library by AndrewFromMelbourne:
https://github.com/AndrewFromMelbourne/raspidmx

Primarily relies on a modified copy of the pngview utility from raspidmx. All other unnescessary files have been omitted.

The battery indicator will be displayed whenever a wireless PS3 controller is connected (using sixad) to the Raspberry Pi. It will run in the background with Emulation Station open as well as when playing games, though the script can be disabled during gameplay if desired.

# How to use

It's important to note that this has only been tested on a Raspberry Pi 3 and relies on the sixad utility for connecting with PS3 controllers. Also, you'll need to have libpng installed if you don't already have it. Enter the following command on your Raspberry Pi:

```
$ sudo apt-get install libpng-dev
```

## Step 1:

Copy these files onto the pi, in a folder that you can remember. For example:

> /home/pi/RetroPie/customscripts/batteryCheck/

The rest of the instructions assume you're using this folder. If not, just make sure to change each instance of the above folder path with your own.

## Step 2:

From the command line on the pi (or through ssh), cd to the folder you copied over:

```
$ cd /home/pi/RetroPie/customscripts/batteryCheck
```

## Step 3:

Type 'make' to compile the code:

```
$ make
```

This will create the executable file that handles the graphical display. The file (called batDisplay, located in the code folder) draws the battery icon on the screen and then ends. Another script (batCheck.py) is used to determine battery levels and trigger the batDisplay executable.

## Step 4:

To test that the code works properly, try:

```
$ ./code/batDisplay ./icons/bat3.png
```

Which (assuming no error messages show up in the terminal) should display a battery icon on the screen the pi is connected to.

## Step 5:

To get the battery display to work with PS3 controllers, the batCheck.py python script needs to be setup to run on startup.
A simple way to handle this is to use the autostart.sh script, found here:

> /opt/retropie/configs/all/autostart.sh

Open this file and add the following lines of code above the emulationstation entry:

```
# Start PS3 controller battery check script
python /home/pi/RetroPie/customscripts/batteryCheck/batCheck.py &
```

That's it! Reboot the pi and the battery check script should be working.
The battery indicator will appear when you first connect a controller.

# Optional (disable during gameplay):

The python script repeatedly monitors the sixad log file to check if new controllers have been connected.
From my testing, the script doesn't seem to have any noticable impact on gameplay performance.
However, just to be sure, it's possible to disable it during gameplay using the runcommand-onstart/runcommand-onend scripts.

To stop the script once a game is opened, navigate to:

> /opt/retropie/configs/all/runcommand-onstart.sh

And add the following code:

```
# Kill the battery checker script when entering games
pkill -f batCheck.py
```

To restart the script after exiting games, open the file:

> /opt/retropie/configs/all/runcommand-onend.sh

And add the following code:

```
# Restart the PS3 controller battery check script
python /home/pi/RetroPie/customscripts/batteryCheck/batCheck.py &
```

Note that every time the battery check is restarted, it will re-report the battery levels. If you don't want this happening,
go back to the autostart script (/opt/retropie/configs/all/autostart.sh) and add the following code above the line
that calls the python script:

```
# Create an empty log file for battery check script
> '/home/pi/RetroPie/customscripts/batteryCheck/batteryCheckLog.temp'
```

This creates an empty log file on startup which the script will detect and use to store a list of controllers already checked.
When the script is restarted after exiting a game, it will use this list to make sure it doesn't re-report the existing controllers.
(Though controllers connected/re-connected during a game will be displayed on exiting the game)

# To uninstall:

Delete the folder containing the files (/home/pi/RetroPie//home/pi/RetroPie/customscripts/batteryCheck)
Then make sure to remove the extra lines added to the autostart.sh, runcommand-onstart.sh and runcommand-onend.sh scripts (located in /opt/retropie/configs/all/)

# Customization

### Battery Icons

They're located in the icons folders, just replace them with whatever .png files you want: you can use transparency and there aren't any restrictions on the image dimensions (at least, keep them smaller than the screen size). Just make sure to keep the same naming convention: bat0.png, bat1.png, .... bat4.png

### Indicator Location/Timing/Speed

Open the batCheck.py script and look for the line with a variable called `dispCmdOptions`
Try changing this to something like:

```
dispCmdOptions = '-x 0 -y 0 -s 1000 -t 6'
```

This will cause the icon to instantly appear (instead of sliding in, due to the large -s value) in the very top left corner of the screen (x=0, y=0), and stay on screen for 6 seconds (the -t option). The full list of options can be found in code folder ReadMe.
