import os
import socket
import packets

from f1_2020_telemetry.packets import unpack_udp_packet

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
		print("Received:", type(packet).__name__)
		# print(packet.header)

		if curr_session_uid != packet.header.sessionUID:

			packet_saver = packets.PacketSaver(packet.header.sessionUID)
			plotting_thread = plotting.PlottingThread(packet.header.sessionUID)

			plotting_thread.start()

		# Save this sessionUID to be able to check if new one has started
		curr_session_uid = packet.header.sessionUID

		# Save the packet
		packet_saver.save(packet)

		# TODO: start plotting thread


if __name__ == '__main__':
	packet_listen()
