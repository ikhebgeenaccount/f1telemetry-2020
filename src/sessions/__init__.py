import os

import pandas as pd

from .session_data import SessionData


def most_recent_session(data_path):
	"""
	:return:The sessionUID of the most recent session.
	"""
	return all_sessions(data_path)['sessionUID'].iloc[-1]


def all_sessions(data_path):
	"""
	Returns a pandas.DataFrame object of datetimes and sessionsUIDs, sorted by date ascending.
	:return: pandas.DataFrame object
	"""
	session_list = pd.read_csv(os.path.join(data_path, 'sessions.csv'))

	return session_list
