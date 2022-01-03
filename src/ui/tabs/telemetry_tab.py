import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from src.ui.tabs.tab_interface import Tab

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class TelemetryTab(QWidget):

	def __init__(self):
		super().__init__()

		self.figure = Figure(figsize=(10, 10))
		self.axes = self.figure.subplots(4, 1, sharex='all')

		# Set ylims for the graphs
		self.axes[0].set_ylim(ymin=0, ymax=375)
		self.axes[1].set_ylim(ymin=0, ymax=1)
		self.axes[2].set_ylim(ymin=0, ymax=1)
		self.axes[3].set_ylim(ymin=0, ymax=8)

		self.plots = [None, None, None, None]

		# Create Matplotlib canvas
		self.canvas = FigureCanvasQTAgg(self.figure)

		# Layout to which QWidgets can be added
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.canvas)
		self.setLayout(self.layout)

		# Data to save
		self.lap_number = -1
		self.track_length = -1

		# y values that will be shown
		self.attrs = ['speed', 'throttle', 'brake', 'gear']
		self.ys = [[], [], [], []]

		# x is the distance into the lap
		self.lap_distance_x = []

		self.timer = QTimer()
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.redraw)
		self.timer.start()

	def update_data(self, packet):
		if packet.header.packetId == 1:
			if self.track_length != packet.trackLength:
				self.track_length = packet.trackLength
				self.axes[0].set_xlim(xmin=0, xmax=self.track_length)
		elif packet.header.packetId == 2:
			self.lap_distance_x.append(packet.lapData[packet.header.playerCarIndex].lapDistance)
			if self.lap_number != packet.lapData[packet.header.playerCarIndex].currentLapNum:
				self.lap_number = packet.lapData[packet.header.playerCarIndex].currentLapNum
				self.ys = [[], [], [], []]
				self.lap_distance_x = []
		elif packet.header.packetId == 6:
			for l, attr in zip(self.ys, self.attrs):
				l.append(getattr(packet.carTelemetryData[packet.header.playerCarIndex], attr))

	def redraw(self):
		# Update plots data with new data, when lengths are equal
		for i in range(len(self.plots)):
			min_length = min(len(self.ys[i]), len(self.lap_distance_x))
			if self.plots[i] is None:
				self.plots[i] = self.axes[i].plot(self.lap_distance_x[0:min_length], self.ys[i][0:min_length])[0]
			else:
				self.plots[i].set_xdata(self.lap_distance_x[0:min_length])
				self.plots[i].set_ydata(self.ys[i][0:min_length])
		self.canvas.draw()

	# TODO: configs for tabs? allows for easier creation of tabs for users?
	def get_title(self):
		return 'Telemetry'
