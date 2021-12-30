import csv
import os
import socket
import sys
from os.path import abspath

import numpy as np
import pandas
from f1_2020_telemetry.packets import unpack_udp_packet
from matplotlib import pyplot as plt

import packets
import plotting
import sessions


def packet_listen(data_path):
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
			print(f'Creating new session stuff with sessionUID {packet.header.sessionUID}\n and packet {packet}')
			packet_saver = packets.PacketSaver(packet.header.sessionUID, data_path)
			plotting_thread = plotting.PlottingThread(packet.header.sessionUID)

			plotting_thread.start()

		# Save this sessionUID to be able to check if new one has started
		curr_session_uid = packet.header.sessionUID

		# Save the packet
		packet_saver.save(packet)


def plot_data(data_path):
	sd = sessions.SessionData(sessions.most_recent_session(data_path), data_path)

	data = sd.load_telemetry(2)

	fig, (ax0, ax1, ax2, ax3) = plt.subplots(4)

	ax0.plot(data['lapDistance'], data['speed'])
	ax1.plot(data['lapDistance'], data['throttle'])
	ax2.plot(data['lapDistance'], data['brake'])
	ax3.plot(data['lapDistance'], data['gear'])

	# TODO: create plot of track and m_worldPosition coords with
	#  https://medium.com/towards-formula-1-analysis/analyzing-formula-1-data-using-python-2021-abu-dhabi-gp-minisector-comparison-3d72aa39e5e8

	plt.show()


if __name__ == '__main__':
	# TODO: create config for save path
	data_root = abspath(os.getcwd())

	if '--record' in sys.argv:
		packet_listen(data_root)
	elif '--plot' in sys.argv:
		plot_data(os.path.join(data_root, 'data'))
