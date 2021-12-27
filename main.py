import csv
import os
import socket
from os.path import abspath

import numpy as np
import pandas
from f1_2020_telemetry.packets import unpack_udp_packet

import packets
import plotting


def packet_listen():
	udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	udp_socket.bind(("", 20777))

	# Initial session is whatever
	curr_session_uid = 0
	packet_saver = None
	plotting_thread = None

	while True:
		udp_packet = udp_socket.recv(2048)
		packet = unpack_udp_packet(udp_packet)

		if curr_session_uid != packet.header.sessionUID:
			# TODO: create config for save path
			packet_saver = packets.PacketSaver(packet.header.sessionUID, abspath(os.getcwd()))
			plotting_thread = plotting.PlottingThread(packet.header.sessionUID)

			plotting_thread.start()

		# Save this sessionUID to be able to check if new one has started
		curr_session_uid = packet.header.sessionUID

		# Save the packet
		packet_saver.save(packet)


if __name__ == '__main__':
	packet_listen()

	# Code below is a test for reading the telemetry csv files that contain arrays.
	# data = pandas.read_csv('test.csv')
	#
	# Convert the string of values to array of floats, per column
	# data['a1'] = data['a1'].apply(np.fromstring, dtype=float, sep=' ')
	# data['a2'] = data['a2'].apply(np.fromstring, dtype=float, sep=' ')
	# data['a3'] = data['a3'].apply(np.fromstring, dtype=float, sep=' ')
	#
	# print(data)
