#!/usr/bin/env python

### this tool allows playback of data in a terminal and physically output to can via comma panda
### currently limited to physical playback of one ID at a time

from __future__ import print_function
import argparse
import numpy as np
import time
from panda import Panda
from bitstring import BitArray as ba 
import struct
import sys
import matplotlib.pyplot as plt

def parse_args():
	arg_parser = argparse.ArgumentParser(description='PandaLogger.py data parser')
	arg_parser.add_argument('-i',  '--input', required=True, help='output file from PandaLogger.py')
	arg_parser.add_argument('-t',  '--testMode', required=False, default=False, help='set to <True> if ack is required')	
	arg_parser.add_argument('-m',  '--mask', required=False, default='0x800', help='play back data only on this identifier <decimal>')	
	arg_parser.add_argument('-r',  '--replay', required=True, default=False, help='play back physical data via CAN')
	arg_parser.add_argument('-s',  '--sleep', required=True, type=float, help='sleep time (ms) between playing messages back')
	arg_parser.add_argument('-pb', '--playbackBus', required=False, default=0, type=int, help='replay bus number if other than bus 0')
	arg_parser.add_argument('-g',  '--grapher', required=False, default=False, help='show plots of individual bytes and "user graphs"')
	arg_parser.add_argument('-b',  '--bus', required=False, default='0', help='choose which can bus to playback or graph data from, 0 / 1 / 2')
	return arg_parser.parse_args()

def main():
	args = parse_args()

	# connect to panda if relay is active
	if args.replay == 'True':
		try:
			print("Trying to connect to Panda over USB...")
			p = Panda()
		
			# clear can data buffers on panda
			p.can_clear(0xffff)
		
		except AssertionError:
			print("USB connection failed.")
			sys.exit(0)

		# turn off CAN tx safety mode
		if args.testMode == 'True':
			p.set_safety_mode(p.SAFETY_ALLOUTPUT)
		elif args.testMode == 'False':
			p.set_safety_mode(p.SAFETY_NOOUTPUT)
		elif args.testMode == 'Bench':
			print('bench test mode engag3d, no safety mode set!!')
		else:
			print("incorrect testMode arguement")
			sys.exit("exiting...")	

	# import text file
	canData = np.genfromtxt(args.input, skip_header=1, delimiter=',', dtype=str) 
	print("data has been imported")

	# num can packets
	numCanPackets = np.size(canData,0)
	print("num can samples: ", numCanPackets)

	time_packets = np.zeros((len(canData),1)) 

	# tesla data only
	veh_speed = np.zeros((len(canData),1)) 
	ap_state = np.zeros((len(canData),1))  
	accel_pedal = np.zeros((len(canData),1)) 
	steer_angle = np.zeros((len(canData),1)) 
	brake_low = np.zeros((len(canData),1)) 
	brake_high = np.zeros((len(canData),1)) 
	brake_pedal_state = np.zeros((len(canData),1))
	drive_torque_uint = np.zeros((len(canData),1))
	drive_torque_int = np.zeros((len(canData),1))
	x2b9_counter = np.zeros((len(canData),1))
	x2b9_accel_max = np.zeros((len(canData),1))
	x2b9_accel_min = np.zeros((len(canData),1))
	x2b9_jerk_max = np.zeros((len(canData),1))
	x2b9_jerk_min = np.zeros((len(canData),1))
	x2b9_aebstate = np.zeros((len(canData),1))	
	x2b9_accstate = np.zeros((len(canData),1))		
	x2b9_speed_request = np.zeros((len(canData),1)) 
	x2b9_speed_error = np.zeros((len(canData),1)) 
	x2bf_counter = np.zeros((len(canData),1))
	x2bf_accel_max = np.zeros((len(canData),1))
	x2bf_accel_min = np.zeros((len(canData),1))
	x2bf_jerk_max = np.zeros((len(canData),1))
	x2bf_jerk_min = np.zeros((len(canData),1))
	x2bf_aebstate = np.zeros((len(canData),1))	
	x2bf_accstate = np.zeros((len(canData),1))		
	x2bf_speed_request = np.zeros((len(canData),1)) 
	x2bf_speed_error = np.zeros((len(canData),1)) 
	x3fa_unknown_request = np.zeros((len(canData),1)) 
	x3fa_unknown_request_int = np.zeros((len(canData),1)) 

	# ford data only
	ford_init_steering_angle = np.zeros((len(canData),1))
	ford_calib_steering_angle = np.zeros((len(canData),1))
	ford_init_steering_angle_no_mask = np.zeros((len(canData),1))
	ford_ws_lf = np.zeros((len(canData),1))
	ford_ws_rf = np.zeros((len(canData),1))
	ford_ws_lr = np.zeros((len(canData),1))
	ford_ws_rr = np.zeros((len(canData),1))
	ford_app = np.zeros((len(canData),1))
	ford_brake_press = np.zeros((len(canData),1))

	# universal data
	data_graph_all = np.zeros((len(canData),1))
	id_graph_all = np.zeros((len(canData),1))
	utc_time_all = np.zeros((len(canData),1))
	utc_time_avg = np.zeros((len(canData),1))

	message_1 = np.zeros((len(canData),1)) # experiment value for plotting
	message_2 = np.zeros((len(canData),1)) # experiment value for plotting
	message_3 = np.zeros((len(canData),1)) # experiment value for plotting
	message_4 = np.zeros((len(canData),1)) # experiment value for plotting
	
	message_0byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_1byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_2byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_3byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_4byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_5byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_6byte = np.zeros((len(canData),1)) # experiment value for plotting
	message_7byte = np.zeros((len(canData),1)) # experiment value for plotting				

	user_message_1 = np.zeros((len(canData),1)) # reference for plots
	user_message_2 = np.zeros((len(canData),1)) # reference for plots
	user_message_3 = np.zeros((len(canData),1)) # reference for plots
	user_message_4 = np.zeros((len(canData),1)) # reference for plots	
	user_message_5 = np.zeros((len(canData),1)) # reference for plots

	zero = np.zeros((len(canData),1))
	frameNumber = 0

	# show current mask called at terminal
	if args.mask is not None:
		print("args mask: ", args.mask)
		maskint = int(args.mask, 0)

	# show current graphing args bus
	if args.grapher is not None:
		print("args graphing bus: ", args.bus)
		args_bus_int = int(args.bus, 0)

	# for loop for iterating through text file
	for i, row in enumerate (canData):
		busNum = row[0]
		messIden = row[1]
		data = row[2]
		length = row[3]
		utc_time = row[4]

		message_id_int = int(messIden,0)
		bus_num_int = int(busNum,0)
		length_int = int(length,0)
		dataInt = int(data,0)

		### physical CAN replay via panda
		if args.replay == 'True':	
			if maskint == 0x800 and bus_num_int == args_bus_int:
				dataStructOut = struct.pack('>Q',dataInt) # '>Q' argument == big endian long struct format
				p.can_send(message_id_int,dataStructOut,args.playbackBus)
				print([(bus_num_int), (messIden), (data), (length_int)])
				time.sleep(args.sleep) # sleep

			elif message_id_int == maskint and bus_num_int == args_bus_int:
				dataStructOut = struct.pack('>I',dataInt) # '>Q' argument == big endian long struct format
				p.can_send(message_id_int,dataStructOut,args.playbackBus)
				print([(bus_num_int), (messIden), (data), (length_int)])								
				time.sleep(args.sleep) # sleep
		
		### terminal playback / debugging ###
		elif args.replay == 'False':
			if maskint == 0x800:
				dataStructOut = struct.pack('>Q',dataInt) # '>Q' argument == big endian long struct format
				print([(bus_num_int), (messIden), (data), (length_int)])			

				time.sleep(args.sleep) # sleep

			elif message_id_int == maskint:
				dataStructOut = struct.pack('>Q',dataInt) # '>Q' argument == big endian 8 byte unsigned // '>I' argument == big endian 4 byte unsigned
				frameNumber = frameNumber+1

				if args.grapher == False: 
					# '{0}\r'.format(x)
					print('{0}\r'.format([(bus_num_int), (messIden), (data), (length_int)], 'frame number: ', frameNumber))

				### tesla vehicle speed ###
				if messIden == '0x155': # wheel speed id
					if bus_num_int == 0:
						b5 = '0x'+(data[:16])[12:] # motec byte offset 5, 16 bit
						wheelSpeed = int(b5,0)*(0.00999999978)
						print([(bus_num_int), (messIden), (data), (length_int)], wheelSpeed)	

				### tesla crc test // CORRECT FOR 0x488 ((byte0 + byte1 + byte2 + id + len)%256) ###
				elif messIden == '0x488': ### AP lateral control ID
					mysteryFactor = 0
					dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
					crc = dataSum%256
	
					if crc != ord(dataStructOut[7]):
						print('wrong crc y0!!!!')
						print('sum: ', dataSum)
						print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
						print('error: ', crc - ord(dataStructOut[7]))
						print([(bus_num_int), (messIden), (data), (length_int)])
					else:
						print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])
		
				### tesla crc test // CORRECT FOR 0x370 ((byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6 + id + len + -5)%256)
				elif messIden == '0x370': 
					mysteryFactor = -5
					dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
					crc = dataSum%256
			
					if crc != ord(dataStructOut[7]):
						print('wrong crc y0!!!!')
						print('sum: ', dataSum)
						print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
						print('error: ', crc - ord(dataStructOut[7]))
						print([(bus_num_int), (messIden), (data), (length_int)])
					else:
						print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])

				### tesla crc test // CORRECT FOR 0x2b9 ((byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6 + id + len + -6)%256)
				elif messIden == '0x2b9': ### AP long command, maybe?
					mysteryFactor = -6
					dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
					crc = dataSum%256
	
					if crc != ord(dataStructOut[7]):
						print('wrong crc y0!!!!')
						print('sum: ', dataSum)
						print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
						print('error: ', crc - ord(dataStructOut[7]))
						print([(bus_num_int), (messIden), (data), (length_int)])	
					else:
						print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])

				### tesla crc test // CORRECT FOR 0x2bf ((byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6 + id + len + -6)%256)
				if 	bus_num_int == 1:
					if messIden == '0x2bf'	:
						mysteryFactor = -12
						dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
						crc = dataSum%256
		
						if crc != ord(dataStructOut[7]):
							print('wrong crc y0!!!!')
							print('sum: ', dataSum)
							print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
							print('error: ', crc - ord(dataStructOut[7]))
							print([(bus_num_int), (messIden), (data), (length_int)])	
						else:
							print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])						

				### tesla crc test // CORRECT FOR 0x175 ((byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6 + id + len + -7)%256)
				elif messIden == '0x175':
					mysteryFactor = -7
					dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
					crc = dataSum%256
			
					if crc != ord(dataStructOut[7]):
						print('wrong crc y0!!!!')
						print('sum: ', dataSum)
						print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
						print('error: ', crc - ord(dataStructOut[7]))
						print([(bus_num_int), (messIden), (data), (length_int)])	
					else:
						print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])

				### tesla crc test // CORRECT FOR 0x238 ((byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6 + id + len + 0)%256)
				if bus_num_int == 1:
					if messIden == '0x238':
						mysteryFactor = 0
						dataSum = mysteryFactor + message_id_int + length_int + ord(dataStructOut[0]) + ord(dataStructOut[1]) + ord(dataStructOut[2]) + ord(dataStructOut[3]) + ord(dataStructOut[4]) + ord(dataStructOut[5]) + ord(dataStructOut[6])
						crc = dataSum%256
				
						if crc != ord(dataStructOut[7]):
							print('wrong crc y0!!!!')
							print('sum: ', dataSum)
							print('this is calculated crc: ', crc, 'this is the last byte: ', ord(dataStructOut[7]))
							print('error: ', crc - ord(dataStructOut[7]))
							print([(bus_num_int), (messIden), (data), (length_int)])	
						else:
							print('crc is correct!', [(bus_num_int), (messIden), (data), (length_int)])

				### ford steering angle print (no crc) ###
				if bus_num_int == 0:
					# elif messIden == '0x76': # recorded directly from panda
					if messIden == '0x076': # converted socketcan only
						_ford_init_steering_angle = ((int(('0x'+data[:6][2:]),0)&0x7fff) - 16000) * 0.1
						_ford_init_steering_angle_no_mask = ((int(('0x'+data[:6][2:]),0)&0xffff) - 16000) * 0.1
						_ford_calib_steering_angle = (((int(('0x'+data[:10][6:]),0)&0xfffe) - 16000) / 2) * 0.1 # unsure if this is real]
						utc_time_all[i:] = utc_time
						utc_time_avg[i:] = 1/(utc_time_all[i] - utc_time_all[i-1])
						# print([(bus_num_int), (messIden), (data), (length_int)], ' init: ', _ford_init_steering_angle, ' no mask: ', _ford_init_steering_angle_no_mask, ' freq: ', utc_time_avg[i])

					### ford wheel angular rate print (no crc) ###
					elif messIden == '0x217':
						_ford_ws_lf = ((int(('0x'+data[:6][2:]),0)&0xfffc)-0) * 0.0040767 # m/s
						_ford_ws_rf = ((int(('0x'+data[:10][6:]),0)&0xfffc)-0) * 0.0040767 # m/s
						_ford_ws_lr = ((int(('0x'+data[:14][10:]),0)&0xfffc)-0) * 0.0040767 # m/s
						_ford_ws_rr = ((int(('0x'+data[:18][14:]),0)&0xfffc)-0) * 0.0040767 # m/s
						utc_time_all[i:] = utc_time
						utc_time_avg[i:] = 1/(utc_time_all[i] - utc_time_all[i-1])
						# print([(bus_num_int), (messIden), (data), (length_int)], ' lr (m/s): ', "{0:.4f}".format(_ford_ws_lr), ' rr (m/s): ', "{0:.4f}".format(_ford_ws_rr), ' freq: ', utc_time_avg[i])				

				time.sleep(args.sleep) # sleep

		'''
		Grapher / Plotter
		'''

		### Tesla Model S Only!!! ###
		if args.grapher == 'True':
			### vehicle speed reference channel ###
			if bus_num_int == 0:
				if messIden == '0x155': ### vehicle speed information
					veh_speed[i:] = (int(('0x'+data[:16][12:]),0)&0xffff)*0.00999999978
			
			if messIden == '0x488': ### autopilot state 
				ap_state[i:] = (int(('0x'+data[:8][6:]),0)&0xC0)
			
			if messIden == '0x108' and bus_num_int == 0: ### drive inverter torque (Nm)
				accel_pedal[i:] = (int(('0x'+data[:16][14:]),0)*2/5)
				b0 = data[2:][:2]
				b1 = data[4:][:2]
				b2 = data[6:][:2]
				b3 = data[8:][:2]
				b4 = data[10:][:2]
				b5 = data[12:][:2]
				b6 = data[14:][:2]
				b7 = data[16:][:2]
				le_data = '0x'+ (b7 + b6 + b5 + b4 + b3 + b2 + b1 + b0)
				drive_torque_uint[i:] = (ba('0x'+le_data[14:][:4]).uint)&0x1fff
				if (drive_torque_uint[i]) > 4095:
					drive_torque_int[i:] = ((drive_torque_uint[i] - 8191)*0.25)
				else:
					drive_torque_int[i:] = drive_torque_uint[i]*0.25

			if messIden == '0x3': ### steering wheel angle (deg)
				steer_angle[i:] = (((int('0x'+data[:6][2:],0)&0x3FFF)/2)-2048)
			
			if messIden == '0x185': ### possible brake pressure measurement or position
				brake_high[i:] = (int(('0x'+data[:8][2:]),0)&0xffffff)
				brake_low[i:] = (int(('0x'+data[:14][8:]),0)&0xffffff)
			
			if messIden == '0x118': ### brake depressed state
				brake_pedal_state[i:] = (int(('0x'+data[:6][4:]),0)&0x80)/128*10000000
			
			if messIden == '0x2b9': ### longitudinal control information
				b0 = data[2:][:2]
				b1 = data[4:][:2]
				b2 = data[6:][:2]
				b3 = data[8:][:2]
				b4 = data[10:][:2]
				b5 = data[12:][:2]
				b6 = data[14:][:2]
				b7 = data[16:][:2]
				le_data = '0x'+ (b7 + b6 + b5 + b4 + b3 + b2 + b1 + b0)
				x2b9_speed_request[i:] = (ba('0x'+le_data[15:][:4]).uint)*0.1
				x2b9_counter[i:] = ((ba('0x'+le_data[4:][:1]).uint)&0xe)>>1 ### counter
				x2b9_accel_max[i:] = ((((ba('0x'+le_data[4:][:3]).uint)&0x1ff)*0.04)-15) ### accelMax
				x2b9_accel_min[i:] = (((((ba('0x'+le_data[7:][:3]).uint)&0xff8)>>3)*0.04)-15) ### accelMin
				x2b9_jerk_max[i:] = ((((ba('0x'+le_data[9:][:3]).uint)&0x7f8)>>3)*0.034) ### jerkMax
				x2b9_jerk_min[i:] = (((((ba('0x'+le_data[11:][:3]).uint)&0x7fc)>>2)*0.018)-9.1) ### jerkMin
				x2b9_aebstate[i:] = ((ba('0x'+le_data[11:][:3]).uint)&0x3) ### aebstate
				x2b9_accstate[i:] = ((ba('0x'+le_data[14:][:1]).uint)) ### accstate

			# if bus_num_int == 1:
				if messIden == '0x2bf': ### longitudinal control information
					b0 = data[2:][:2]
					b1 = data[4:][:2]
					b2 = data[6:][:2]
					b3 = data[8:][:2]
					b4 = data[10:][:2]
					b5 = data[12:][:2]
					b6 = data[14:][:2]
					b7 = data[16:][:2]
					le_data = '0x'+ (b7 + b6 + b5 + b4 + b3 + b2 + b1 + b0)
					x2bf_speed_request[i:] = (ba('0x'+le_data[15:][:4]).uint)*0.1
					x2bf_counter[i:] = ((ba('0x'+le_data[4:][:1]).uint)&0xe)>>1 ### counter
					x2bf_accel_max[i:] = ((((ba('0x'+le_data[4:][:3]).uint)&0x1ff)*0.04)-15) ### accelMax
					x2bf_accel_min[i:] = (((((ba('0x'+le_data[7:][:3]).uint)&0xff8)>>3)*0.04)-15) ### accelMin
					x2bf_jerk_max[i:] = ((((ba('0x'+le_data[9:][:3]).uint)&0x7f8)>>3)*0.034) ### jerkMax
					x2bf_jerk_min[i:] = (((((ba('0x'+le_data[11:][:3]).uint)&0x7fc)>>2)*0.018)-9.1) ### jerkMin
					x2bf_aebstate[i:] = ((ba('0x'+le_data[11:][:3]).uint)&0x3) ### aebstate
					x2bf_accstate[i:] = ((ba('0x'+le_data[14:][:1]).uint)) ### accstate
				
				if accel_pedal[i] != 0:
					x2bf_speed_error[i:] = 0
				else:
					x2bf_speed_error[i:] = veh_speed[i]- x2bf_speed_request[i]

			if messIden == '0x3fa': ### unknown long control
				b0 = data[2:][:2]
				b1 = data[4:][:2]
				b2 = data[6:][:2]
				b3 = data[8:][:2]
				b4 = data[10:][:2]
				b5 = data[12:][:2]
				b6 = data[14:][:2]
				b7 = data[16:][:2]
				le_data = '0x'+ (b7 + b6 + b5 + b4 + b3 + b2 + b1 + b0)					
				x3fa_unknown_request[i:] = (ba('0x'+b1+b0).uint)&0x1ff
				if x3fa_unknown_request[i] > 256:
					x3fa_unknown_request_int[i:] = (x3fa_unknown_request[i]-512.0)*0.1
				else:
					x3fa_unknown_request_int[i:] = (x3fa_unknown_request[i])*0.1			

			### Ford F150 Only!! ###
			if bus_num_int == 0:
				# if messIden == '0x76': # recorded directly from panda
				if messIden == '0x076': # converted socketcan format
					### ford f150 steering wheel angle units in degrees ###
					ford_init_steering_angle[i:] = ((int(('0x'+data[:6][2:]),0)&0x7fff) - 16000) * 0.1
					ford_init_steering_angle_no_mask[i:] = ((int(('0x'+data[:6][2:]),0)&0xffff) - 16000) * 0.1
					
				if messIden == '0x217':
					### claimed units to be rad/sec
					### assuming tire circumfrence of 2.56 meters
					### assuming tire radius of 0.40767 meters
					### rad/sec * radius = meters/sec
					ford_ws_lf[i:] = ((int(('0x'+data[:6][2:]),0)&0xfffc)-0) * 0.0040767 # m/s
					ford_ws_rf[i:] = ((int(('0x'+data[:10][6:]),0)&0xfffc)-0) * 0.0040767 # m/s
					ford_ws_lr[i:] = ((int(('0x'+data[:14][10:]),0)&0xfffc)-0) * 0.0040767 # m/s
					ford_ws_rr[i:] = ((int(('0x'+data[:18][14:]),0)&0xfffc)-0) * 0.0040767 # m/s	

				if messIden == '0x204':
					### units in percentage ###
					ford_app[i:] = (int(('0x'+data[:6][2:]),0) & 0x01ff)

				if messIden == '0x07d':
					### unknown units ###
					ford_brake_press[i:] = (int(('0x'+data[:6][2:]),0) & 0xffff)

			### data aggregators for plotting later
			if message_id_int == maskint and bus_num_int == args_bus_int:
				data_graph_all[i:] = dataInt
				id_graph_all[i:] = message_id_int

				if length_int == 8:	
					### two byte messages ###
					# message_1[i:] = ba('0x'+data[:6][2:]).uint 
					message_1[i:] = ba('0x'+data[:6][2:]).uint
					message_2[i:] = ba('0x'+data[:10][6:]).uint 
					message_3[i:] = ba('0x'+data[:14][10:]).uint 
					message_4[i:] = ba('0x'+data[:18][14:]).uint
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint 
					message_3byte[i:] = ba('0x'+data[:10][8:]).uint
					message_4byte[i:] = ba('0x'+data[:12][10:]).uint
					message_5byte[i:] = ba('0x'+data[:14][12:]).uint										
					message_6byte[i:] = ba('0x'+data[:16][14:]).uint 										
					message_7byte[i:] = ba('0x'+data[:18][16:]).uint	

					### user messages for experimentation ###	
					user_message_1[i:] = (int(('0x'+data[:6][2:]),0) & 0xffff)

					### little endian experimentation ###
					# b0_hex = '0x'+b0
					# b1_hex = '0x'+b1
					# b2_hex = '0x'+b2
					# b3_hex = '0x'+b3
					# b4_hex = '0x'+b4
					# b5_hex = '0x'+b5
					# b6_hex = '0x'+b6
					# b7_hex = '0x'+b7
					# int_b0 = int(b0_hex,0)
					# int_b1 = int(b1_hex,0)
					# int_b2 = int(b2_hex,0)
					# int_b3 = int(b3_hex,0)
					# int_b4 = int(b4_hex,0)
					# int_b5 = int(b5_hex,0)
					# int_b6 = int(b6_hex,0)
					# int_b7 = int(b7_hex,0)
					



				elif length_int == 7:
					### two byte messages ###
					message_1[i:] = ba('0x'+data[:6][2:]).uint
					message_2[i:] = ba('0x'+data[:10][6:]).uint
					message_3[i:] = ba('0x'+data[:14][10:]).uint
					### single byte messages ###					
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint
					message_3byte[i:] = ba('0x'+data[:10][8:]).uint
					message_4byte[i:] = ba('0x'+data[:12][10:]).uint
					message_5byte[i:] = ba('0x'+data[:14][12:]).uint										
					message_6byte[i:] = ba('0x'+data[:16][14:]).uint						
				
				elif length_int == 6:
					### two byte messages ###
					message_1[i:] = ba('0x'+data[:6][2:]).uint
					message_2[i:] = ba('0x'+data[:10][6:]).uint
					message_3[i:] = ba('0x'+data[:14][10:]).uint
					### single byte messages ###					
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint
					message_3byte[i:] = ba('0x'+data[:10][8:]).uint
					message_4byte[i:] = ba('0x'+data[:12][10:]).uint
					message_5byte[i:] = ba('0x'+data[:14][12:]).uint		

				elif length_int == 5:
					### two byte messages ###
					message_1[i:] = ba('0x'+data[:6][2:]).uint
					message_2[i:] = ba('0x'+data[:10][6:]).uint
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint
					message_3byte[i:] = ba('0x'+data[:10][8:]).uint
					message_4byte[i:] = ba('0x'+data[:12][10:]).uint

				elif length_int == 4:
					### two byte messages ###
					message_1[i:] = ba('0x'+data[:6][2:]).uint
					message_2[i:] = ba('0x'+data[:10][6:]).uint
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint
					message_3byte[i:] = ba('0x'+data[:10][8:]).uint
					user_message_1[i:] = (int('0x'+(data[:10][8:])+(data[:8][6:]),0))

				elif length_int == 3:
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint
					message_2byte[i:] = ba('0x'+data[:8][6:]).uint					

				elif length_int == 2:
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						
					message_1byte[i:] = ba('0x'+data[:6][4:]).uint

				elif length_int == 1:
					### single byte messages ###
					message_0byte[i:] = ba('0x'+data[:4][2:]).uint						

				else:
					print('something is br0k3 y0...')
					sys.exit(0)

	print('avg frequency for ', args.mask, ' at ', np.average(utc_time_avg), 'hz')

	### show plots ###	
	if args.grapher == 'True':		

		plt.style.use('dark_background')

		fig1, (msg1_a, msg2_a, msg3_a, msg4_a, msg5_a, msg6_a, msg7_a, msg8_a) = plt.subplots(8,1, sharex=True)
		fig1.suptitle('8 bit messages')
		msg1_a.plot(message_0byte, label='byte 0')
		msg1_a.legend()
		msg2_a.plot(message_1byte, label='byte 1')
		msg2_a.legend()
		msg3_a.plot(message_2byte, label='byte 2')	
		msg3_a.legend()
		msg4_a.plot(message_3byte, label='byte 3')
		msg4_a.legend()
		msg5_a.plot(message_4byte, label='byte 4')
		msg5_a.legend()
		msg6_a.plot(message_5byte, label='byte 5')
		msg6_a.legend()
		msg7_a.plot(message_6byte, label='byte 6')
		msg7_a.legend()
		msg8_a.plot(message_7byte, label='byte 7')
		msg8_a.legend()

		fig2, (umsg1, msg1, msg2, msg3, msg4) = plt.subplots(5, 1, sharex=True)
		fig2.suptitle('16 bit messages')
		umsg1.plot(user_message_1 , label='user message 1')
		umsg1.legend()
		msg1.plot(message_1, label='byte 0+1')
		msg1.legend()
		msg2.plot(message_2, label='byte 2+3')
		msg2.legend()
		msg3.plot(message_3, label='byte 4+5')
		msg3.legend()
		msg4.plot(message_4, label='byte 6+7')
		msg4.legend()

		fig3, (msg1, msg2, msg3, msg4, time_plt) = plt.subplots(5,1,sharex=True)
		fig3.suptitle('ford message guesses')
		msg1.plot(ford_init_steering_angle_no_mask, label='steering angle no mask (f150) degrees')
		msg1.legend()
		msg2.plot(ford_ws_lf * 2.237, label='left front wheel speed (f150) mph')
		msg2.plot(ford_ws_rf * 2.237, label='right front wheel speed (f150) mph')
		msg2.plot(ford_ws_lr * 2.237, label='left rear wheel speed (f150) mph')
		msg2.plot(ford_ws_rr * 2.237, label='right rear wheel speed (f150) mph')						
		msg2.legend()
		msg3.plot(ford_app * 0.1953125, label='app %')
		msg3.legend()
		msg4.plot(ford_brake_press * 0.02, label='brake press (unitless)')
		msg4.legend()
		time_plt.plot(utc_time_avg, label='update frequency (s)')
		time_plt.legend()

		plt.show()

	# re-enable safety mode when playback is complete
	if args.replay == 'True':
		p.set_safety_mode(p.SAFETY_NOOUTPUT)
		print('panda saftey mode re-enabled')
	else:
		print('playback finished...')

if __name__=='__main__':
	main()
