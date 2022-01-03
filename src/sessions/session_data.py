import os

import pandas as pd
import numpy as np


class SessionData:
	"""
	SessionData handles all data loading for a session that has happened in the past.
	"""

	def __init__(self, session_uid, data_path):
		self.telemetry_data = None
		self.data_path = data_path
		self.session_uid = session_uid

	def load_telemetry(self, lap_number, session_type='timetrial'):
		"""
		Loads the telemetry data for specified lap number and session type.
		Return object is a DataFrame containing all telemetry data.
		:param lap_number: Lap number for which to load telemetry data
		:param session_type: Session type containing that lap number
		:return: pandas.DataFrame object
		"""
		# Read all four types of telemetry data
		telemetry = pd.read_csv(os.path.join(self.data_path, str(self.session_uid), str(session_type), 'player', f'lap{lap_number}_telemetry.csv'))
		motion = pd.read_csv(os.path.join(self.data_path, str(self.session_uid), str(session_type), 'player', f'lap{lap_number}_motion.csv'))
		status = pd.read_csv(os.path.join(self.data_path, str(self.session_uid), str(session_type), 'player', f'lap{lap_number}_status.csv'))
		lap_data = pd.read_csv(os.path.join(self.data_path, str(self.session_uid), str(session_type), 'player', f'lap{lap_number}_data.csv'))

		# Merge the DataFrames on sessionTime
		t_data = telemetry.merge(motion, how='inner', on=['sessionTime', 'frameIdentifier'])
		tt_data = t_data.merge(status, how='inner', on=['sessionTime', 'frameIdentifier'])
		# Final result should be sorted
		self.telemetry_data = tt_data.merge(lap_data, how='outer', on=['sessionTime', 'frameIdentifier'], sort=True)

		# TODO: columns containing strings should be converted to np arrays
		# # Convert the string of values to array of floats, per column
		# data['a1'] = data['a1'].apply(np.fromstring, dtype=float, sep=' ')
		# data['a2'] = data['a2'].apply(np.fromstring, dtype=float, sep=' ')
		# data['a3'] = data['a3'].apply(np.fromstring, dtype=float, sep=' ')
		#
		# print(data)

		return self.telemetry_data

	def session_info(self, session_type):
		pass

	def session_types(self):
		"""
		:return: List of all session types for this sessionUID
		"""
		pass

