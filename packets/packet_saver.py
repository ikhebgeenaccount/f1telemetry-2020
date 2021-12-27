import logging
import os

import numpy as np

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
							From CarTelemetry
							(session_time, frame_identifier, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs,
							brakes_temps, tyre_surf_temps, tyre_inner_temps, engine_temp, tyres_pressures, surface_types
							From CarStatus
							session_time, frame_identifier, fuel_mix, fuel_amount, tyres_wear, tyre_compound, tyre_compound_visual,
							tyres_damage, tyre_age_laps, front_wing_left_dmg, front_wing_right_dmg, rear_wing_dmg, drs_fault,
							engine_dmg, gear_box_dmg, ers_store, ers_deploy_mode, mguk_harvest_this_lap, mguh_harvest_this_lap,
							ers_deployed_this_lap
							From LapData
							session_time, frame_identifier, lap_distance)
							From Motion
							session_time, frame_identifier, m_worldPositionX, m_worldPositionY, m_worldPositionZ, m_gForceLateral,
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
		self.SESSION_TYPE_ID_MATCH = {
			0: 'unknown',
			1: 'fp1',
			2: 'fp2',
			3: 'fp3',
			4: 'short practice',
			5: 'q1',
			6: 'q2',
			7: 'q3',
			8: 'short quali',
			9: 'oneshot quali',
			10: 'race',
			11: 'race2',
			12: 'timetrial'
		}

		# Sets logging up and points it to save_path/logs/[sessionUID].log
		# TODO: create log file?
		logging.basicConfig(filename=os.path.join(save_path, 'logs', f'{session_uid}.log'), level=logging.DEBUG,
							format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

		self._session_uid = session_uid

		# Indicates whether the session info. like track, type, laps, etc, has been saved yet or not
		self._session_info_saved = False
		self._participants_data_saved = False

		# Save path points to the sessionUID folder, not a session type, this is handled in _write_to_file()
		self._save_path = os.path.join(save_path, 'data', str(session_uid))
		# Create the sessionUID folder
		try:
			os.mkdir(self._save_path)
		except FileExistsError:
			logging.warning(f'{self._save_path} already exists.')

		# Save the lap number of current lap
		self._lap_number = 0
		# Save array of drivers
		self._drivers = []
		self._player_driver_index = -1  # Indicates what index of self._drivers is the player

		# Tracks the session type (FP1/2/3, Q, R), on change creates new folder
		self._session_type = -1

		# Data arrays that are saved every so often
		self._telemetry = ''  # Saved at the start of every new lap, or when retiring

		# Loads config of what fields to save
		self._packet_config = PacketConfig(os.path.join(save_path, 'cfg', 'packet_keys.ini'))

		# TODO: create sessions.csv in /data to save date and other stuff per session uid?

	def save(self, packet):
		"""
		Saves the data from the packet.
		:param packet:
		:return:
		"""
		self._player_driver_index = packet.header.playerCarIndex
		self._PACKET_ID_MATCH[packet.header.packetId](packet)
		logging.info(f'Received packet with packetId {packet.header.packetId} at sessionTime {packet.header.sessionTime}'
					 f' and frameIdentifier {packet.header.frameIdentifier}.')

	def _write_to_file(self, file, data):
		"""
		Saves the data to the file. File path must be relative path starting from sessionUID/sessionType.
		E.g., if file = 'player/lap4_telemetry.csv', it will be stored in '[sessionUID]/[sessionType]/player/lap4_telemetry.csv'.
		If there already exists a file at the location, the data will be appended to the existing file. If no file exists,
		the file is created, after which the data is written to it.
		:param file: Relative path
		:param data: String to store in file
		:return:
		"""
		logging.info(f'Saving data to file {file}, data = {data[0:10]} ... {data[-10:-1]}')
		path = os.path.join(self._save_path, self.SESSION_TYPE_ID_MATCH[self._session_type], file)

		if os.path.exists(path):
			# Append if file exists
			with open(path, 'a') as f:
				f.write(data)
		else:
			# Create file if not exists
			with open(path, 'w') as f:
				f.write(data)

	def motion_packet(self, packet):
		logging.info(f'Processing motion packet.')
		# TODO
		pass

	def session_packet(self, packet):
		logging.info(f'Processing session packet.')
		# If sessionType has changed, create a new folder and update current session_type,
		if packet.sessionType != self._session_type:
			new_path = os.path.join(self._save_path, self.SESSION_TYPE_ID_MATCH[packet.sessionType], 'player')
			# Creates [save_path]/[sessionType]/player, since player will always exist
			os.makedirs(new_path, exist_ok=True)
			self._session_type = packet.sessionType

			# New session type needs its participants and info saved again
			self._session_info_saved = False
			self._participants_data_saved = False

		# TODO: save current track circumstances

		# Save one time session info
		if not self._session_info_saved:
			# Create string with all data that needs to be saved based on self._packet_config
			fields_to_save = self._packet_config.get_fields('session_packet')
			# First line is field names preceded by a #
			save_string = f'#{self._packet_config.get_fields("session_packet", list_format=False)}\n'
			save_string += self._retrieve_attr(packet, fields_to_save)

			self._write_to_file('session.csv', save_string[:-1])

			# Session info has been saved
			self._session_info_saved = True

	def lap_data_packet(self, packet):
		logging.info(f'Processing lap data packet.')
		# TODO: lap date indicates current lap number and pit status

		# TODO: change in lap number means save telemetry (lapX.csv) and save times to laps.csv
		#  or when retiring save as well (based on m_resultStatus)
		# Change in lap number indicates new lap has been started and telemetry from previous lap can be written to disk
		if packet.lapData[self._player_driver_index].currentLapNum != self._lap_number:
			self._write_to_file(os.path.join('player', f'lap{self._lap_number}_telemetry.csv'), self._telemetry)
			self._telemetry = ''

			# self._lap_number = packet.lapData[self._player_driver_index].currentLapNum

	def event_packet(self, packet):
		logging.info(f'Processing event packet.')
		# TODO: save event to events.csv, how to handle different types of events in packet_keys.ini?
		pass

	def participants_packet(self, packet):
		"""
		Saves the current list of participants to self._drivers
		:param packet:
		:return:
		"""
		logging.info(f'Processing participants packet.')
		if packet.numActiveCars != len(self._drivers):
			logging.warning(f'Number of active drivers changed from {len(self._drivers)} to {packet.numActiveCars}.')
			self._drivers = packet.participants

		if not self._participants_data_saved:
			fields_to_save = self._packet_config.get_fields('participant_data')
			save_string = f'#{self._packet_config.get_fields("participant_data", list_format=False)}\n'

			for pd in packet.participants:
				save_string += self._retrieve_attr(pd, fields_to_save)

			self._write_to_file('participants.csv', save_string)

			self._participants_data_saved = True

	def car_setups_packet(self, packet):
		logging.info(f'Processing car setups packet.')
		# TODO: maybe save just player setup?
		pass

	def car_telemetry_packet(self, packet):
		logging.info(f'Processing car telemetry packet.')
		# If telemetry is empty, create the first line of the save file with the field names
		if self._telemetry == '':
			self._telemetry = '#sessionTime,frameIdentifier,' + self._packet_config.get_fields('car_telemetry_data', list_format=False) + '\n'

		fields_to_save = self._packet_config.get_fields('car_telemetry_data')
		save_string = f'{packet.header.sessionTime},{packet.header.frameIdentifier},'

		save_string += self._retrieve_attr(packet.carTelemetryData[self._player_driver_index], fields_to_save)

		self._telemetry += save_string[:-1]

	def car_status_packet(self, packet):
		logging.info(f'Processing car status packet.')
		# TODO: how to combine telemetry and status and write them at once?  <-- but now this needs solving
		#  need to check if status and telemetry have different sessionTime or not
		#  could be packets are created at same time ingame just sent at different times?  <-- THIS IS THE CASE
		pass

	def final_classification_packet(self, packet):
		logging.info(f'Processing final classification packet.')
		fields_to_save = self._packet_config.get_fields('final_classification_data')
		save_string = ''
		for i, d in enumerate(packet.classificationData):
			save_string += f'{self._drivers[i].driverId},{self._drivers[i].name},{self._drivers[i].raceNumber},'

			save_string += self._retrieve_attr(d, fields_to_save)

		field_names = 'driverId,name,raceNumber,' + self._packet_config.get_fields('final_classification_data', False)
		save_string = '#' + field_names + '\n' + save_string

		self._write_to_file('final_classification.csv', save_string)

	def lobby_info_packet(self, packet):
		logging.info(f'Processing lobby info packet.')
		pass

	def _retrieve_attr(self, structure, fields, newline=True):
		"""
		Retrieves all fields in fields from the data structure. Returns their values in a comma separated string.
		:param structure: Structure containing key value pairs
		:param fields: Keys for which the value to retrieve
		:return: A single string with the values of the keys separated by commas
		"""
		save_string = ''
		for f in fields:
			# If it's an array, decode it into an array
			if 'Array' in type(getattr(structure, f)).__name__:
				# Arrays are saved as follows:
				# Let array to be saved be [0.1, 2., 3., 0.6]
				# Then the string corresponding to the value of the field that is being saved will be
				# 0.1 2. 3. 0.6
				# This can be read and decoded back to arrays using pandas DataFrames and numpy as follows
				# data = pandas.read_csv('data.csv')
				# data['a1'] = data['a1'].apply(np.fromstring, dtype=float, sep=' ')
				# where 'a1' is the field that has arrays as data values
				save_string += str(np.ctypeslib.as_array(getattr(structure, f)))[1:-1]
				# [1:-1] is to remove the brackets []
			else:  # Otherwise, it's either a byte string or some other type, like int, float, ...
				try:  # Attempts to decode a byte string
					save_string += str(getattr(structure, f).decode('utf-8')) + ','
				except (UnicodeDecodeError, AttributeError):  # If it's not a string, just get the value
					save_string += str(getattr(structure, f)) + ','

		# Return save_string save the last comma
		if newline:
			return save_string[:-1] + '\n'
		else:
			return save_string[:-1]
