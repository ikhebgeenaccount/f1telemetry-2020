import os
import socket
import packet_save

from f1_2020_telemetry.packets import unpack_udp_packet

PACKET_ID_MATCH = {
	0: packet_save.motion_packet,
	1: packet_save.session_packet,
	2: packet_save.lap_data_packet,
	3: packet_save.event_packet,
	4: packet_save.participants_packet,
	5: packet_save.car_setups_packet,
	6: packet_save.car_telemetry_packet,
	7: packet_save.car_status_packet,
	8: packet_save.final_classification_packet,
	9: packet_save.lobby_info_packet
}


def packet_listen():
	udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	udp_socket.bind(("", 20777))

	# Initial session is whatever
	curr_sessionUID = 0

	while True:
		udp_packet = udp_socket.recv(2048)
		packet = unpack_udp_packet(udp_packet)
		print("Received:", type(packet).__name__)
		print(packet.header)

		# If this sessionUID is different from previous packet sessionUID, make a new folder for the new session
		if curr_sessionUID != packet.header.sessionUID:
			# Make dir
			os.mkdir(f'packets/{packet.header.sessionUID}')

		# Send packet to correct packet handler based on packet id
		PACKET_ID_MATCH[packet.header.packetId](packet)

		# TODO: save packets to folders with names of sessionUID
		# TODO: how to save them? split them into csvs per packettype? will be a mess with drivers through eachother
		# TODO: plot data in realtime

		# Save this sessionUID to be able to check if new one has started
		curr_sessionUID = packet.header.sessionUID


if __name__ == '__main__':
	# packet_listen()
	pass