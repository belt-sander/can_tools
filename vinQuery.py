#!/usr/bin/env python3

import can
import yaml
import sys
import argparse

def parse_args():
	arg_parser = argparse.ArgumentParser(description='query vin experiment tool')
	arg_parser.add_argument('-chan', '--channel', default='can0', help='name of socketcan interface (default: can0)')
	arg_parser.add_argument('-config', '--config_file', required=True, help='location of vehicle setup file (.yaml)')
	return arg_parser.parse_args()

class Send():
	def __init__(self):
		args = parse_args()
		self.bus = can.Bus(interface='socketcan', channel=args.channel, recieve_own_messages=True)
		self.tx_id = None
		self.tx_len = None
		self.tx_data = None

	def send_query(self):
		request_11_bit = can.Message(arbitration_id=0x7DF, is_extended_id=False , data=[0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
		self.bus.send(request_11_bit, timeout=0.2)
		request_29_bit = can.Message(arbitration_id=0x18DAF10E, is_extended_id=True, data=[0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
		self.bus.send(request_29_bit, timeout=0.2)

	def send_flow_control(self):
		flow_control_11_bit = can.Message(arbitration_id=0x7E0, is_extended_id=False, data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
		self.bus.send(flow_control_11_bit, timeout=0.2)
		flow_control_29_bit = can.Message(arbitration_id=0x18DAF10F, is_extended_id=True, data=[0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
		self.bus.send(flow_control_29_bit, timeout=0.2)


class Read():
	def __init__(self):
		args = parse_args()
		f = open(args.config_file)
		self.yaml_file = yaml.load(f)
		self.bus = can.Bus(interface='socketcan', channel=args.channel, recieve_own_messages=True)
		self.rx_id = None
		self.rx_len = None
		self.rx_data = None

	def data_msg(self):
		while True:
			try:
				data_frame = self.bus.recv()
				self.rx_id = data_frame.arbitration_id 
				self.rx_len = len(data_frame.data)
				self.rx_data = data_frame.data
				
				self.vin_11_bit_read()
				# self.vin_29_bit_read()

			except KeyboardInterrupt:
				print(' ...exiting...')
				sys.exit(0)

	def vin_11_bit_read(self):
		_step = 0
		if self.rx_id == 2024: ### 0x7E8	
			# print('rx: ', self.rx_data)
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
				'''				
				+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
				| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12| 13| 14| 15| 16| 17|   
				+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
				|   WMI     |         VDS           |             VIS               |
				+-----------+-------------------+---+---+---+-----------------------+
				|   manf    |   vehicle type    | CS| MY| PC|   sequential number   |
				+-----------+-------------------+---+---+---+-----------------------+
				'''
				vin_hex = (self.vin_a + self.vin_b + self.vin_c + self.vin_d + self.vin_e + self.vin_f + self.vin_g + self.vin_h + self.vin_i + self.vin_j + self.vin_k + self.vin_l + self.vin_m + self.vin_n + self.vin_o + self.vin_p + self.vin_q)
				vin_byte = bytes.fromhex(vin_hex)
				vin_ascii = vin_byte.decode("ASCII")
				serial = vin_ascii[9:][:8] # Indvidual Serial Number
				year = vin_ascii[9:][:1] # Letter Year
				veh_descriptor = vin_ascii[3:][:5] # Vehicle Descriptor
				wmi = vin_ascii[:3] # World Manufacturer Identifier

				year_dict = {'Y': [2000], '1': [2001], '2': [2002], '3': [2003], '4': [2004],
							'5': [2005], '6': [2006], '7': [2007], '8': [2008], '9': [2009],
							'A': [2010], 'B': [2011], 'C': [2012], 'D': [2013], 'E': [2014],
							'F': [2015], 'G': [2016], 'H': [2017], 'J': [2018], 'K': [2019]}

				print('vin: ', vin_ascii)
				print('serial: ', serial)
				print('year: ', year_dict[year])
				print('veh_descriptor: ', veh_descriptor)
				print('wmi: ', wmi, '\n')

				config_vin = self.yaml_file['id']['vin']

				if vin_ascii == config_vin:
					valid = True
					print('VIN matched to configuration file.', '\n')
				else:
					valid = False
					print('no VIN match for configuration file.', '\n')
					print('configuration file VIN is:', config_vin, '\n')
					print('exiting...', '\n')

				sys.exit(0)

	### TODO: Add 29-bit support ###
	# def vin_29_bit_read(self):
	# 	if self.rx_id == 417001742: ### 0x18DAF10E
	# 		for i in range(self.rx_len):
	# 			print('id: ', hex(self.rx_id), ' len: ', self.rx_len, ' byte: ',[i] ,hex(self.rx_data[i]))

def main():
	args = parse_args()	
	send = Send()
	read = Read()

	send.send_query()
	read.data_msg()

if __name__ == "__main__":
	main()