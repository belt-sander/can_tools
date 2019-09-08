#!/usr/bin/env python

### proxy forwarder test

from panda import Panda
import argparse
import sys, traceback
import time
import binascii
import struct
from bitstring import BitArray as ba

def parse_args():
	arg_parser = argparse.ArgumentParser(description='recieved can data forwarder from bus 0 to bus 1')
	arg_parser.add_argument('-t',
							'--testMode',
							required=True,
							help='set to <True> if ack is required')
	return arg_parser.parse_args()

def panda_open():
	args = parse_args()

	try:
		print("Trying to connect to Panda over USB...")
		p = Panda()

		p.can_clear(0xffff)
		print('can ringbuffer cleared')

	except AssertionError:
		print("USB connection failed.")
		sys.exit(0)

		args = parse_args()

	if args.testMode == "True":
		p.set_safety_mode(p.SAFETY_ALLOUTPUT)
	elif args.testMode == "False":
		p.set_safety_mode(p.SAFETY_NOOUTPUT)
	else:
		print("incorrect testMode arguement")
		sys.exit("exiting...")
	print('ready for data...')
	return p

def main():
	args = parse_args()
	p = panda_open()

	### can forwarder settings ###
	# p.set_can_forwarding(0,1)
	# print 'forwarder enabled can_0 -> can_1'
	p.set_can_forwarding(1,0)
	print 'forwarder enabled can_1 -> can_0'

	controlReqCount = 0
	controlReqMessage = False
	newNonApChassisMessage = False

	while True:
		inputData = p.can_recv()

		for address, _, dat, src  in inputData:

			### AP exploit request monitor ###
			if src == 2 and address == 0x118 and dat[0] == 100:
				controlReqMessage = True				
				if controlReqMessage == True:
					controlReqCount = controlReqCount + 1
					print'control request counter: ', controlReqCount
					print'control req state: ', controlReqMessage

			### AP exploit control packet from controller ###
			if src == 2 and address == 0x488:
				apExploitFrame = ba('0x'+binascii.hexlify(dat)).int
				apExploitFramePack = struct.pack('>I',apExploitFrame)
				# print'vella controller message: ', [str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)]

			### basic forwarder / chassis -> AP ###
			if src == 0:
				newNonApChassisMessage = True
				if newNonApChassisMessage == True:
					if address == 0x488 and controlReqMessage == False:
						p.can_send(address, str(dat), 1)
					elif address != 0x488 and controlReqMessage == False:
						p.can_send(address, str(dat), 1)
					else:
						p.can_send(0x488, apExploitFramePack, 1)
						controlReqMessage = False

					newNonApChassisMessage = False
					
					# print'chassis bus message: ', [str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)]							

					# if controlReqMessage == True and src == 0 and address != 0x488:
					# 	p.can_send(0x488, apExploitFramePack, 1)		
					# else:
					# 	p.can_send(address, str(dat), 1)
					# controlReqMessage = False


			### experiments / tests ###
			# if src == 0 and address == 0x666:
			# 	newSend = True				
			# 	if newSend == True:
			# 		print'input data: ', inputData
			# 		print'converted output: ', [str(src), str(hex(address)), "0x" + binascii.hexlify(dat), len(dat)]		
			# 		print'addr: ', address
			# 		print'send state: ', newSend					
			# 		count = count + 1
			# 		print'counter: ', count

			# 		### simple test moving byte 0,1 to positon 6,7 ###
			# 		db = '0x' + binascii.hexlify(dat)
			# 		dbm = '0x'+'00'+'00'+'00'+'00'+'00'+'00'+db[:6][2:]
			# 		dbmi = int(dbm,0)
			# 		dbmip = struct.pack('>Q', dbmi)
			# 		p.can_send(address, dbmip,1)

if __name__ == "__main__":
		main()