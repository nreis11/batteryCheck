
import os
import time
import re
import sys

# Specify sixad log file path
logPath='/var/log/sixad'

# Specify battery check display file path
dispExecPath='./code/batDisplay'
dispCmdOptions = '' # Example: '-x 32 -y 32 -s 32 -t 3'

# Get current directory. Icons and check log are stored relative to this python file
currentDirectory = os.path.dirname(os.path.realpath(sys.argv[0]))

# Path for logging battery checks. Logging will be enable if this file exists
batLog = currentDirectory + '/batteryCheckLog.temp'
batLogEnable = 0

# Path for battery icons (including the 'bat' part of bat_.png file name for convenience)
iconPath = currentDirectory + '/icons/bat'

# Debugging enable/disable
__debug = 0


# *****************************************************************************************************************
# ***************************************** Useful Functions ******************************************************

# Define a function for reading the log file in reverse (efficiently)
# Found: https://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python (Author: Berislav Lopac)
def readlines_reverse(filename):
	charCount = 0
	with open(filename) as qfile:
		qfile.seek(0, os.SEEK_END)
		position = qfile.tell()
		line = ''
 		while position >= 0:
			qfile.seek(position)
			next_char = qfile.read(1)
			if next_char == "\n":
				yield line[::-1]
				line = ''
			else:
				line += next_char
			position -= 1
			charCount += 1
		yield line[::-1]

# Define a function for checking if a PID is running
def checkPID(PIDstr):
	if os.path.exists('/proc/' + PIDstr):
		return 1
	else:
		return 0


# Define function for loading in PID lists from a log file
def loadPIDFile(enableThis):
	outputList = []
	if enableThis:
		# First check if any PID values were logged from a previous copy of this script
		with open(batLog, 'r') as file_handler:
		    for line in file_handler: 
			if line.strip() is not '': outputList.append(line.strip())
	return outputList


# Define function for updating the PID list file
def updatePIDFile(inputList, enableThis):
	if enableThis:
		with open(batLog, 'w') as file_handler:
			for listItem in inputList:
				file_handler.write("{}\n".format(listItem))


# Regular expression used to extract square bracketed sections
extractSqBrackets = re.compile(r'\[([^][]+)\]')


# *****************************************************************************************************************
# *****************************************************************************************************************


# First check if any PID values were logged from a previous copy of this script (if logging is enabled)
if os.path.exists(batLog): batLogEnable = 1
pidList = loadPIDFile(batLogEnable)

if __debug:
	print 'BatteryLog Enable: ' + str(batLogEnable)
	print 'Initial PID list:'
	print pidList


# Record time stamp of the log file (looking for changes)
last_stamp = -1;
time_stamp = os.stat(logPath).st_mtime;


# Now loop forever, checking for changes (battery notifications) to the sixad log file
while 1:
	if time_stamp != last_stamp:

		if __debug: print 'Time stamp change detected'


# *****************************************************************************************************************
# ************************************ Extract last lines of log file *********************************************


		# Extract text after the last 'Watching... (5s)' entry, since this indicates controllers can connect
		lastText = []
		lineCount = 0
		for line in readlines_reverse(logPath):
			if 'Watching' in line:
				# Stop if we see the 'Watching' string, since that should be the newest data since reboot
				break
			else:
				# Only care about lines containing battery information, so only store these lines
				if 'Battery' in line:
					lastText.append(line)

		# Un-reverse the last lines of the log file so that we maintain chronological ordering of controller connects
		lastText = lastText[::-1]



# *****************************************************************************************************************
# ************************************ Report battery for running PIDs ********************************************

		# Print out the last lines of text
		for line in lastText:
	
			# Now dealing with only lines containing battery info. Typically look like:
			# sixad-sixaxis[###]: Connected 'PLAYSTATION(R)3 Controller (XX:XX:XX:XX:XX:XX)' [Battery ##]
			# The first ### is the PID number, the second ## is the battery value (typically EE, 02, 03, 04, 05)

			# Pull the data out of square brackets
			getBrackets = extractSqBrackets.findall(line)

			# The first square brackets contain the pid
			pidVal = getBrackets[0]

			# Check if PID is running
			if checkPID(pidVal):

				if __debug: print 'PID ' + pidVal + ' is running'

				# Process is running. Only display battery info if it's not in our already displayed list
				if pidVal not in pidList:

					if __debug: print 'PID ' + pidVal + ' is not in PID list'
					# Get battery value for display
					batVal = getBrackets[1][-1:]

					# Check that it is a number
					if batVal.isdigit():
						batVal = int(batVal)
					else:
						batVal = 0

					# Normal value range is 2 - 5. The display program shows 1, 2 3 or 4 'charge blocks' (i.e. 25%, 50%, 75%, 100%)
					batVal = batVal - 1
					if batVal < 0: batVal = 0
					if batVal > 4: batVal = 4

					# Call the battery display function					
					dispCmd = dispExecPath + ' ' + dispCmdOptions + ' ' + iconPath + str(batVal) + '.png'
					if __debug: print 'calling display function: ' + dispCmd
					os.system(dispCmd)

					# Add PID to displayed list so we don't repeatedly display it
					pidList.append(pidVal)
					updatePIDFile(pidList, batLogEnable)

					if __debug:
						print 'New pidList:'
						print pidList
					
			

			else:

				if __debug: print 'PID ' + pidVal + ' is not running'

				# PID is not running. Check if it was on the already displayed list
				if pidVal in pidList:
					pidList.remove(pidVal)
					updatePIDFile(pidList, batLogEnable)

					if __debug:
						print 'New pidList:'
						print pidList

# ************************************************************************************************************************************

	else:

		if __debug: print 'No time stamp change'


	# Update time stamps
	last_stamp = time_stamp
	time_stamp = os.stat(logPath).st_mtime

	# Wait around for a few seconds
	time.sleep(2)
