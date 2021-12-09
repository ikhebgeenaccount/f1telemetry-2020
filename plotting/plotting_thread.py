from threading import Thread

import matplotlib.pyplot as plt


class PlottingThread(Thread):

	def __init__(self, session_uid):
		"""

		:param session_uid:
		"""
		Thread.__init__(self)

		self.session_uid = session_uid
