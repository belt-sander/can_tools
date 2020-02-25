#!/usr/bin/env python3

### can receive module ###

from pyvit import can
from pyvit.hw import socketcan
import os
import time
import argparse

def main():
	# bring up can interface device
	os.system("sudo /sbin/ip link set can0 up type can bitrate 1000000")
	print("if no errors above, can device up at can0")
	print("can baud rate set to 1000kbps")

	# associate device with "can0"
	dev = socketcan.SocketCanDev("can0")
	dev.start()

	# ready for messages
	print("ready and waiting for data...")

	while True:
		print("new message: ", dev.recv())

if __name__ == "__main__":
	main()
