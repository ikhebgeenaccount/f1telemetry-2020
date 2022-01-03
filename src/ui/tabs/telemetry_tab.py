from PyQt5.QtWidgets import QTabWidget

from src.ui.tabs.tab_interface import Tab


class TelemetryTab(QTabWidget, Tab):

	def __init__(self):
		super().__init__()

	def update_data(self, packet):
		pass