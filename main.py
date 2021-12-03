import socket

from f1_2020_telemetry.packets import unpack_udp_packet

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))

while True:
	udp_packet = udp_socket.recv(2048)
	packet = unpack_udp_packet(udp_packet)
	print("Received:", type(packet).__name__)
	print()

	# TODO: save packets to folders with names of sessionUID
	# TODO: how to save them? split them into csvs per packettype? will be a mess with drivers through eachother
	# TODO: plot data in realtime
