import configparser
import os

import ids

import logging

from packets.packet_config import PacketConfig


class PacketSaver:

	def __init__(self, session_uid, save_path):
		"""
		PacketSaver handles the saving of packets. The following folder structure is created by PacketSaver:

		|--- sessions
			|--- sessionUID
				|--- session_type
					events.csv
					final_classification.csv
						(position, driver_id, driver_name, num_laps, grid_pos, points, num_pit_stops, result_status)
					participants.csv
						(driver_id, name, number, ai_controlled, telemetry_setting)
					session.csv
						(track_id, laps, session_type, formula, track_length, pit_speed_limit, network_game)
					session_evolution.csv
						(session_time, weather, air_temp, track_temp, safety_car)
					|--- player
						driver.data
							(name, setup)
						laps.csv
							(lap_number, s1_time, s2_time, s3_time, tyre, invalid, pitting)  TODO: pit status?
						lap1_telemetry.csv
							(session_time, frame_identifier, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs,
							brakes_temps, tyre_surf_temps, tyre_inner_temps, engine_temp, tyres_pressures, surface_types)
						lap1_status.csv
							(session_time, frame_identifier, fuel_mix, fuel_amount, tyres_wear, tyre_compound, tyre_compound_visual,
							tyres_damage, tyre_age_laps, front_wing_left_dmg, front_wing_right_dmg, rear_wing_dmg, drs_fault,
							engine_dmg, gear_box_dmg, ers_store, ers_deploy_mode, mguk_harvest_this_lap, mguh_harvest_this_lap,
							ers_deployed_this_lap)
						lap1_lap_data.csv
							(session_time, frame_identifier, lap_distance)
						lap1_motion.csv
							(session_time, frame_identifier, m_worldPositionX, m_worldPositionY, m_worldPositionZ, m_gForceLateral,
							m_gForceLongitudinal, m_gForceVertical)
							TODO: create plot of track and m_worldPosition coords with
								https://medium.com/towards-formula-1-analysis/analyzing-formula-1-data-using-python-2021-abu-dhabi-gp-minisector-comparison-3d72aa39e5e8
						...
						lapN.csv
					|--- driver_id
						driver.data
						laps.csv
						lap0.csv
							if applicable, is formation lap
						lap1.csv
						...
						lapN.csv
		:param session_uid:
		:param save_path: Path where session data will be saved. Preferably an absolute path.
		"""
		# Dictionary to match packet ids to saving methods
		self._PACKET_ID_MATCH = {
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

		# Sets logging up and points it to save_path/logs/[sessionUID].log
		logging.basicConfig(filename=os.path.join(save_path, 'logs', f'{session_uid}.log'), level=logging.DEBUG)

		self._session_uid = session_uid

		# Indicates whether the session info. like track, type, laps, etc, has been saved yet or not
		self._session_info_saved = False
		self._participants_data_saved = False

		self._save_path = os.path.join(save_path, 'data', session_uid)
		try:
			os.mkdir(self._save_path)
		except FileExistsError:
			logging.warning(f'{self._save_path} already exists.')

		# Save the lap number of current lap
		self._lap_number = 0
		# Save array of drivers
		self._drivers = []
		self._player_driver_index = -1

		# Tracks the session type (FP1/2/3, Q, R), on change creates new folder
		self._session_type = -1

		# Data arrays that are saved every so often
		self._telemetry = ''  # Saved at the start of every new lap, or when retiring

		# Loads config of what fields to save
		self._packet_config = PacketConfig(os.path.join(save_path, 'cfg', 'packet_keys.ini'))

	def save(self, packet):
		"""
		Saves the data from the packet.
		:param packet:
		:return:
		"""
		self._player_driver_index = packet.header.playerCarIndex
		self._PACKET_ID_MATCH[packet.header.packetId](packet)

	def _write_to_file(self, file, data):
		"""
		Saves the data to the file. File path must be relative path starting from sessionUID/sessionType.
		I.e., if file = 'player/lap4_telemetry.csv', it will be stored in 'sessionUID/sessionType/player/lap4_telemetry.csv'.
		:param file: Relative path
		:param data: String to store in file
		:return:
		"""
		path = os.path.join(self._save_path, str(self._session_type), file)

		if os.path.exists(path):
			# Append if file exists
			with open(path, 'a') as f:
				f.write(data)
		else:
			# Create file if not exists
			with open(path, 'w') as f:
				f.write(data)

	def motion_packet(self, packet):
		# TODO
		pass

	def session_packet(self, packet):
		# If sessionType has changed, create a new folder and update current session_type
		if packet.sessionType != self._session_type:
			os.mkdir(os.path.join(self._save_path, self._session_uid, packet.sessionType))
			self._session_type = packet.sessionType

		# TODO: save current track circumstances

		# Save one time session info
		if not self._session_info_saved:
			fields_to_save = self._packet_config.get_fields('session_packet')
			save_string = f'#{self._packet_config.get_fields("session_packet", list_format=False)}\n'
			for f in fields_to_save:
				save_string += getattr(packet, f) + ','

			self._write_to_file()

	def lap_data_packet(self, packet):
		# TODO: lap date indicates current lap number and pit status

		# TODO: change in lap number means save telemetry (lapX.csv) and save times to laps.csv
		#  or when retiring save as well (based on m_resultStatus)
		if packet.lapData[self._player_driver_index].currentLapNum != self._lap_number:
			self._write_to_file(os.path.join('player', f'lap{self._lap_number}_telemetry.csv'), self._telemetry)
			self._telemetry = ''
		pass

	def event_packet(self, packet):
		# TODO: save event to events.csv
		pass

	def participants_packet(self, packet):
		"""
		Saves the current list of participants to self._drivers
		:param packet:
		:return:
		"""
		if packet.numActiveCars != len(self._drivers):
			logging.warning(f'Number of active drivers changed from {len(self._drivers)} to {packet.numActiveCars}.')
			self._drivers = packet.participants

		if not self._participants_data_saved:
			pass

	def car_setups_packet(self, packet):
		# TODO: maybe save just player setup?
		pass

	def car_telemetry_packet(self, packet):
		# If telemetry is empty, create the first line of the save file with the field names
		if self._telemetry == '':
			self._telemetry = '#sessionTime,frameIdentifier,' + self._packet_config.get_fields('car_telemetry_data', list_format=False) + '\n'

		fields_to_save = self._packet_config.get_fields('car_telemetry_data')
		save_string = f'{packet.header.sessionTime},{packet.header.frameIdentifier},'

		for f in fields_to_save:
			save_string += getattr(packet.carTelemetryData[self._player_driver_index], f) + ','

		self._telemetry += save_string

	def car_status_packet(self, packet):
		# TODO: how to combine telemetry and status and write them at once?
		pass

	def final_classification_packet(self, packet):
		fields_to_save = self._packet_config.get_fields('final_classification_data')
		save_string = ''
		for i, d in enumerate(packet.classificationData):
			save_string += f'{self._drivers[i].driverId},{self._drivers[i].name},{self._drivers[i].raceNumber},'
			for f in fields_to_save:
				save_string += str(getattr(d, f)) + ','
			save_string += '\n'

		field_names = 'driverId,name,raceNumber,' + self._packet_config.get_fields('final_classification_data', False)
		save_string = '#' + field_names + '\n' + save_string

		self._write_to_file('final_classification.csv', save_string)

	def lobby_info_packet(self, packet):
		pass
