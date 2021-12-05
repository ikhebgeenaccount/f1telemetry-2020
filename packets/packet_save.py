import ids


# TODO: how to save them? split them into csvs per packettype? will be a mess with drivers through eachother
def save(packet):
	PACKET_ID_MATCH[packet.header.packetId](packet)


def motion_packet(packet):
	pass


def session_packet(packet):
	# TODO: I think this one contains the array of vehicles, thus the array that is necessary to identify who is who
	#  in all other packets as well
	pass


def lap_data_packet(packet):
	pass


def event_packet(packet):
	pass


def participants_packet(packet):
	pass


def car_setups_packet(packet):
	pass


def car_telemetry_packet(packet):
	# TODO: most important one
	pass


def car_status_packet(packet):
	pass


def final_classification_packet(packet):
	pass


def lobby_info_packet(packet):
	pass


PACKET_ID_MATCH = {
	0: motion_packet,
	1: session_packet,
	2: lap_data_packet,
	3: event_packet,
	4: participants_packet,
	5: car_setups_packet,
	6: car_telemetry_packet,
	7: car_status_packet,
	8: final_classification_packet,
	9: lobby_info_packet
}