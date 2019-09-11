#!/usr/bin/env python

### can logger using comma panda

from __future__ import print_function
import argparse
import numpy as np
import binascii
import csv
import sys
from panda import Panda

def parse_args():
	arg_parser = argparse.ArgumentParser(description='log can data using comma.ai panda and export to txt')

	arg_parser.add_argument('-o',
                          '--outputFileArg', 
                          required=True, 
                          help='txt file output path')
	arg_parser.add_argument('-t',
													'--testMode',
													required=True,
													help='set to <True> if ack is required')
	arg_parser.add_argument('-m',
													'--mask',
													required=False,
													help='set to only log / display data from a particular identifier e.g. <0x666>')
	return arg_parser.parse_args()

def can_logger():
	args = parse_args()
	# translate user input from mask arg to dec
	# argId = int(args.mask, 0)

	try:
		print("Trying to connect to Panda over USB...")
		p = Panda()
	except AssertionError:
		print("USB connection failed.")
		try:
			p = Panda("WIFI")
		except:
			print("WiFi connection timed out. Please make sure your Panda is connected and try again.")
			sys.exit(0)

	# turn off safety mode
	if args.testMode == "True":
		p.set_safety_mode(p.SAFETY_ALLOUTPUT)
	elif args.testMode == "False":
		p.set_safety_mode(p.SAFETY_NOOUTPUT)
	else:
		print("incorrect testMode arguement")
		sys.exit("exiting...")

	# set bus speeds. nominally 500kbps
	# p.set_can_speed_kbps(0,1000)	
	# p.set_can_speed_kbps(1,1000)
	# p.set_can_speed_kbps(2,1000)

	try:
		p.can_clear(0xffff)	
		outputfile = open(args.outputFileArg, 'wb')
		csvwriter = csv.writer(outputfile)
		csvwriter.writerow(['Bus', 'MessageID', 'Message', 'MessageLength'])
		print("Writing csv file to", args.outputFileArg, "Press Ctrl-C to exit...\n")
		
		bus0_msg_cnt = 0
		bus1_msg_cnt = 0
		bus2_msg_cnt = 0

		while True:
			can_recv = p.can_recv()

			for address, _, dat, src  in can_recv:
				if args.mask is None:
					csvwriter.writerow([str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)])
					print([str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)])

					if src == 0:
						bus0_msg_cnt += 1
					elif src == 1:
						bus1_msg_cnt += 1
					elif src == 2:
						bus2_msg_cnt += 1

				if args.mask is not None:
					# address filtering ...
					if address == argId:
						csvwriter.writerow([str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)])
						print([str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)])

						if src == 0:
							bus0_msg_cnt += 1
						elif src == 1:
							bus1_msg_cnt += 1
						elif src == 2:
							bus2_msg_cnt += 1

	except KeyboardInterrupt:
		# turn off output mode
		p.set_safety_mode(p.SAFETY_NOOUTPUT)

		print("\nNow exiting. Final message Counts... Bus 0: " + str(bus0_msg_cnt) + " Bus 1: " + str(bus1_msg_cnt) + " Bus 2: " + str(bus2_msg_cnt))
		outputfile.close()
			
if __name__ == "__main__":
		can_logger()