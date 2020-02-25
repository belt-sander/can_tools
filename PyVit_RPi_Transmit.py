#!/usr/bin/env python3

### can transmit module ###

from pyvit import can
from pyvit.hw import socketcan
import os
import time
import argparse

def parse_args():
	# determine how many messages to send
	arg_parser = argparse.ArgumentParser(description='tool to send can messages')
	arg_parser.add_argument('-n', '--num', type=int, required=True, help='number of messages to send') 
	arg_parser.add_argument('-f', '--freq', type=float, required=False, default=0.1, help='sleep time between mess tx')
	return arg_parser.parse_args()

def main():
	# parse args
	args = parse_args()

	# bring up can interface device
	os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
	print("if no errors above, can device up at can0")
	print("can baud rate set to 500kbps")

	# associate device with "can0"
	dev = socketcan.SocketCanDev("can0")
	dev.start()

	i = 0

	while i < (args.num):
		i = i+1
		frame = can.Frame(0x666)
		if (i >= 255):
			frame.data = [255, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
		else:
			frame.data = [i, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
		dev.send(frame)
		print("frame" ,i, "sent")
		time.sleep(args.freq)

	print(i, "frames sent")

if __name__ == "__main__":
	main()