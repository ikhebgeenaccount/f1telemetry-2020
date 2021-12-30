import csv
import os
import socket
import sys
from os.path import abspath

import numpy as np
import pandas
from f1_2020_telemetry.packets import unpack_udp_packet
from matplotlib import pyplot as plt, cm
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection

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
			# TODO: check what happens with the empty session folder when closing session
			packet_saver = packets.PacketSaver(packet.header.sessionUID, data_path)
			plotting_thread = plotting.PlottingThread(packet.header.sessionUID)

			plotting_thread.start()

		# Save this sessionUID to be able to check if new one has started
		curr_session_uid = packet.header.sessionUID

		# Save the packet
		packet_saver.save(packet)


def plot_data(data_path):
	sd = sessions.SessionData(3737230889795252704, data_path)
	# sd = sessions.SessionData(9607873297504516202, data_path)
	# sd = sessions.SessionData(11541244035795733387, data_path)

	data = sd.load_telemetry(lap_number=4)

	fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, sharex=True)

	ax0.plot(data['lapDistance'], data['speed'])
	ax1.plot(data['lapDistance'], data['throttle'])
	ax2.plot(data['lapDistance'], data['brake'])
	ax3.plot(data['lapDistance'], data['gear'])

	fig, ax = plt.subplots()

	x = np.array(data['worldPositionX'])
	y = np.array(data['worldPositionZ'])

	points = np.array([x, y]).T.reshape(-1, 1, 2)
	segments = np.concatenate([points[:-1], points[1:]], axis=1)

	cmap = cm.get_cmap('viridis', 8)
	lc_comp = LineCollection(segments, cmap=cmap, norm=plt.Normalize(1, cmap.N+1))
	lc_comp.set_array(data['gear'])
	lc_comp.set_linewidth(5)

	ax.add_collection(lc_comp)
	ax.axis('equal')
	# For some reason, tracks are mirroed so unmirror it by inverting an axis
	ax.invert_yaxis()
	# ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

	sm = ScalarMappable(cmap=cmap, norm=plt.Normalize(1, cmap.N + 1))
	fig.colorbar(sm)

	plt.show()


if __name__ == '__main__':
	# TODO: create config for save path
	data_root = abspath(os.getcwd())

	if '--record' in sys.argv:
		packet_listen(data_root)
	elif '--plot' in sys.argv:
		plot_data(os.path.join(data_root, 'data'))
