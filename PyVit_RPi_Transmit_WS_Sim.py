#!/usr/bin/env python3

### can transmit wheel speed emulation module ###

from pyvit import can
from pyvit.hw import socketcan
import os
import time
import argparse

def parse_args():
	# determine how many messages to send
	arg_parser = argparse.ArgumentParser(description='tool to send can messages')
	arg_parser.add_argument('-n', '--num', type=int, required=True, help='number of messages to send') 
	arg_parser.add_argument('-f', '--freq', type=float, required=False, default=0.01, help='sleep time between mess tx (default 0.01 seconds / 100hz)')
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

	speed = 0
	i = 0

	while i < (args.num):
		speed = speed+1
		i = i+1
		
		# address / ID
		frame = can.Frame(0x202)
		
		# split can speed in to two bytes
		speed_a = (speed & 0xff00) >> 8
		speed_b = (speed & 0x00ff) 
	
		# data frame		
		frame.data = [speed_a, speed_b, speed_a, speed_b, speed_a, speed_b, speed_a, speed_b,]

		dev.send(frame)
		print("frame" , i , "sent")
		print("speed value (m/s): ", speed/100)
		time.sleep(args.freq)

	print(i, "frames sent")

if __name__ == "__main__":
	main()
