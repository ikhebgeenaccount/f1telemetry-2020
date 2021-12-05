import os
import socket
import packets

from f1_2020_telemetry.packets import unpack_udp_packet


def packet_listen():
	udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	udp_socket.bind(("", 20777))

	# Initial session is whatever
	curr_session_uid = 0

	while True:
		udp_packet = udp_socket.recv(2048)
		packet = unpack_udp_packet(udp_packet)
		print("Received:", type(packet).__name__)
		print(packet.header)

		# If this sessionUID is different from previous packet sessionUID, make a new folder for the new session
		if curr_session_uid != packet.header.sessionUID:
			# Make dir
			# TODO: needs check? what happens if mkdir a dir that already exists?
			os.mkdir(f'packets/{packet.header.sessionUID}')

			# TODO: start some kind of plotting thread?

		# Save the packet
		packets.save(packet)
		# TODO: plot data in realtime

		# Save this sessionUID to be able to check if new one has started
		curr_session_uid = packet.header.sessionUID


if __name__ == '__main__':
	packet_listen()
