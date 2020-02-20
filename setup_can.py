#!/usr/bin/env python3

from pyvit import can
from pyvit.hw import socketcan
import os
import time
import argparse
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 6666
MESSAGE = "y0, s000n!"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

def udp_rx():
  while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print ("received message:"), data

def udp_tx():
  print("UDP target IP:"), UDP_IP
  print("UDP target port:"), UDP_PORT
  print("message:"), MESSAGE
  sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

def can_rx():
  # bring up can interface devices
  os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
  print("if no errors above, can device up at can0")
  print("can baud rate set to 500kbps")

  os.system("sudo /sbin/ip link set can1 up type can bitrate 500000")
  print("if no errors above, can device up at can1")
  print("can baud rate set to 500kbps")

  # associate device with "can0"
  dev = socketcan.SocketCanDev("can0")
  dev.start()

  # ready for messages
  print("ready and waiting for data...")

  while True:
    print("new message: ", dev.recv())

def main():
  can_rx()

if __name__ == "__main__":
  main()
