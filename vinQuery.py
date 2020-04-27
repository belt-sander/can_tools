#!/usr/bin/env python3

from pyvit import can
from pyvit.hw import socketcan
from bitstring import BitArray as ba
import os
import sys
import time	
import argparse
import numpy as np

def parse_args():
	arg_parser = argparse.ArgumentParser(description='query vin experiment tool')
	arg_parser.add_argument('-c', '--channel', default='vcan0', help='name of socketcan interface (default: vcan0)')
	arg_parser.add_argument('-b', '--baud', type=int, default=500000, help='baud rate of desired can interface (default: 500000)')
	return arg_parser.parse_args()

def bring_up_interface():
	args = parse_args()
	
	if args.channel == 'can0':
		os.system(f'sudo /sbin/ip link set {args.channel} up type can bitrate {args.baud}')
	elif args.channel == 'vcan0':
		os.system('sudo ip link add dev vcan0 type vcan')
		os.system('sudo ip link set up vcan0')
	else:
		print('...something went wrong...')
		sys.exit(0)

	interface = socketcan.SocketCanDev(args.channel)
	interface.start()
	return interface

class Send():
	def __init__(self):
		self.tx_id = None
		self.tx_len = None
		self.tx_data = None

	def send_query(self):
		interface  = bring_up_interface()

		frame_11_bit = can.Frame(0x7DF)
		frame_11_bit.data = [0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]

		frame_29_bit = can.Frame(0x18DAF10E, extended=True)
		frame_29_bit.data = [0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]

		interface.send(frame_11_bit)
		interface.send(frame_29_bit)

	def send_flow_control(self):
		interface = bring_up_interface()

		frame_11_bit_flow_control = can.Frame(0x7E0)
		frame_11_bit_flow_control.data = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

		interface.send(frame_11_bit_flow_control)

class Read():
	def __init__(self):
		self.rx_id = None
		self.rx_len = None
		self.rx_data = None

	def data_msg(self):
		interface = bring_up_interface()

		while True:
			try:
				data_frame = interface.recv()
				self.rx_id = data_frame.arb_id 
				self.rx_len = len(data_frame.data)
				self.rx_data = data_frame.data
				
				self.vin_11_bit_read()
				self.vin_29_bit_read()

			except KeyboardInterrupt:
				print(' ...exiting...')
				sys.exit(0)

	def vin_11_bit_read(self):
		_step = 0

		if self.rx_id == 2024: ### 0x7E8	
			_type = str(hex(self.rx_data[0])) + str(hex(self.rx_data[1])[2:]) # First two bytes of response (0x1014)
			_reply = str(hex(self.rx_data[2])) # Reply to 0x09 PID request (0x49)
			_reply_msg = str(hex(self.rx_data[3])) # Reply to 0x02 PID (0x02)
			_sof = str(hex(self.rx_data[4])) # Usually reports 0x01
			_mutliplex_id = str(hex(self.rx_data[0]))

			if _type == '0x1014' and _reply == '0x49' and _reply_msg == '0x2':
				self.vin_a = str(hex(self.rx_data[5])[2:]) 
				self.vin_b = str(hex(self.rx_data[6])[2:])
				self.vin_c = str(hex(self.rx_data[7])[2:])
				send = Send()
				send.send_flow_control()
				_step = 1
		
			if _mutliplex_id == '0x21':
				self.vin_d = str(hex(self.rx_data[1])[2:])
				self.vin_e = str(hex(self.rx_data[2])[2:])
				self.vin_f = str(hex(self.rx_data[3])[2:])
				self.vin_g = str(hex(self.rx_data[4])[2:])
				self.vin_h = str(hex(self.rx_data[5])[2:])
				self.vin_i = str(hex(self.rx_data[6])[2:])
				self.vin_j = str(hex(self.rx_data[7])[2:])																
				_step = 2

			if _mutliplex_id == '0x22':
				self.vin_k = str(hex(self.rx_data[1])[2:])
				self.vin_l = str(hex(self.rx_data[2])[2:])
				self.vin_m = str(hex(self.rx_data[3])[2:])
				self.vin_n = str(hex(self.rx_data[4])[2:])
				self.vin_o = str(hex(self.rx_data[5])[2:])
				self.vin_p = str(hex(self.rx_data[6])[2:])
				self.vin_q = str(hex(self.rx_data[7])[2:])																
				_step = 3

			if _step == 3:			
				vin_hex = (self.vin_a + self.vin_b + self.vin_c + self.vin_d + self.vin_e + self.vin_f + self.vin_g + self.vin_h + self.vin_i + self.vin_j + self.vin_k + self.vin_l + self.vin_m + self.vin_n + self.vin_o + self.vin_p + self.vin_q)
				print('vin hex: ', vin_hex)
				vin_byte = bytes.fromhex(vin_hex)
				vin_ascii = vin_byte.decode("ASCII")
				print('vin: ', vin_ascii)
				print('done yo. ')
				sys.exit(0)


	def vin_29_bit_read(self):
		if self.rx_id == 417001742: ### 0x18DAF10E
			for i in range(self.rx_len):
				print('id: ', hex(self.rx_id), ' len: ', self.rx_len, ' byte: ',[i] ,hex(self.rx_data[i]))

def main():
	args = parse_args()

	bring_up_interface()
	
	send = Send()
	read = Read()

	send.send_query()
	read.data_msg()

if __name__ == "__main__":
	main()