from threading import Thread

import matplotlib.pyplot as plt


class PlottingThread(Thread):

	def __init__(self, session_uid):
		"""

		:param session_uid:
		"""
		Thread.__init__(self)

		self.session_uid = session_uid

	# TODO:	telemetry plot x: distance, y: brake, throttle, speed

	# TODO: PyQt4 for UI? dropdowns and shit to select drivers, laps, stats, etc

	# TODO: UIs for practice, quali, race

	# TODO: predefined graphs and tables?
	#  perhaps some kind of configs that are interpreted by a UI something
