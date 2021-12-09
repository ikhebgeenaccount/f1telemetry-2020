import os

import ids


class PacketSaver:

	def __init__(self, session_uid):
		"""
		PacketSaver handles the saving of packets. The following folder structure is created by PacketSaver:

		|--- sessions
			|--- sessionUID
				|--- session_type
					events.csv
					final_classification.csv
						(position, driver_id, num_laps, grid_pos, points, num_pit_stops, result_status
					session.data
						(track, laps, session_type, formula, network_game)
					session_evolution.csv
						(weather, air_temp, track_temp, safety_car)
					participants.csv
						(driver_id, name, number, ai_controlled, telemetry_setting)
					|--- player
						driver.data
							(name, setup)
						laps.csv
							(lap_number, s1_time, s2_time, s3_time, tyre, invalid, pitting)  # TODO: pit status?
						lap0.csv
							if applicable, is formation lap  # TODO: how to see if formation lap?
						lap1.csv
							From car telemetry
							(session_time, frame_identifier, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs,
							brakes_temps, tyre_surf_temps, tyre_inner_temps, engine_temp, tyres_pressures, surface_types,
							From car status
							fuel_mix, fuel_amount, tyres_wear, tyre_compound, tyre_compound_visual, tyres_damage, tyre_age_laps,
							front_wing_left_dmg, front_wing_right_dmg, rear_wing_dmg, drs_fault, engine_dmg, gear_box_dmg,
							ers_store, ers_deploy_mode, mguk_harvest_this_lap, mguh_harvest_this_lap, ers_deployed_this_lap)
						...
						lapN.csv
					|--- driver_id
						driver.data
						laps.csv
							(name, other stuff?)
						lap0.csv
							if applicable, is formation lap
						lap1.csv
						...
						lapN.csv
		:param session_uid:
		"""
		# Dictionary to match packet ids to saving methods
		self.PACKET_ID_MATCH = {
			0: self.motion_packet,
			1: self.session_packet,
			2: self.lap_data_packet,
			3: self.event_packet,
			4: self.participants_packet,
			5: self.car_setups_packet,
			6: self.car_telemetry_packet,
			7: self.car_status_packet,
			8: self.final_classification_packet,
			9: self.lobby_info_packet
		}

		self.session_uid = session_uid
		# TODO: needs check? what happens if mkdir a dir that already exists?
		os.mkdir(f'packets/{session_uid}')

		# Save the lap number of current lap
		self.lap_number = 0
		# Save array of drivers
		self.drivers = []

	def save(self, packet):
		"""
		:param packet:
		:return:
		"""
		self.PACKET_ID_MATCH[packet.header.packetId](packet)

	def motion_packet(self, packet):
		pass

	def session_packet(self, packet):
		# TODO: save single use info for session.data

		# TODO: check sessiontype (change?) and create folder for sessiontype in sessionuid folder if not there yet

		# TODO: save current track circumstances
		pass

	def lap_data_packet(self, packet):
		# TODO: lap date indicates current lap number and pit status
		pass

	def event_packet(self, packet):
		# TODO: save event to events.csv
		pass

	def participants_packet(self, packet):
		# TODO: contains the list of participants. which needs to be saved to self.drivers
		pass

	def car_setups_packet(self, packet):
		# TODO: maybe save just player setup?
		pass

	def car_telemetry_packet(self, packet):
		# TODO: most important one
		pass

	def car_status_packet(self, packet):
		# TODO: how to combine telemetry and status and write them at once?
		pass

	def final_classification_packet(self, packet):
		# TODO: save final classification to final_classification.csv
		pass

	def lobby_info_packet(self, packet):
		pass
