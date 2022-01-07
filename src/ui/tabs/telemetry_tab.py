import logging
import math

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QListWidget

from src.ui.tabs.tab_interface import Tab

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class TelemetryTab(QWidget):

	def __init__(self):
		super().__init__()

		# Layout to which QWidgets can be added
		self.layout = QtWidgets.QHBoxLayout()

		# Data to save
		self.cur_lap_number = 0
		self.track_length = -1

		self.lap_times = []

		self.attrs = ['speed', 'throttle', 'brake', 'gear']
		# y values for each attribute, for each lap
		self.ys = [[[], [], [], []]]

		# x is the distance into the lap
		self.lap_distance_x = [[]]

		# Elements are added in order
		self._create_lap_list()
		self._create_mpl_canvas()

		self.setLayout(self.layout)

	def _create_mpl_canvas(self):
		self.figure = Figure(figsize=(10, 10))
		self.axes = self.figure.subplots(4, 1, sharex='all')

		# Set ylims for the graphs
		self.axes[0].set_ylim(ymin=0, ymax=375)
		self.axes[1].set_ylim(ymin=0, ymax=1)
		self.axes[2].set_ylim(ymin=0, ymax=1)
		self.axes[3].set_ylim(ymin=0, ymax=8)

		# TODO: labels
		# for i, attr in enumerate(self.attr):
		# 	self.axes[i].set_ylabel()

		self.plots = [None, None, None, None]

		# Create Matplotlib canvas
		self.canvas = FigureCanvasQTAgg(self.figure)

		self.layout.addWidget(self.canvas, 4)

	def _create_lap_list(self):
		self.lap_list = QListWidget()

		font = self.lap_list.font()
		font.setPointSize(22)
		self.lap_list.setFont(22)

		self.layout.addWidget(self.lap_list, 1)

	def update_data(self, packet):
		if packet.header.packetId == 1:
			# Session packet, has track length data
			if self.track_length != packet.trackLength:
				self.track_length = packet.trackLength
				self.axes[0].set_xlim(xmin=0, xmax=self.track_length)
		elif packet.header.packetId == 2:
			# Lap data packet, has current lap number and lap distance
			self.lap_distance_x[self.cur_lap_number].append(packet.lapData[packet.header.playerCarIndex].lapDistance)
			# If a new lap has been started, and the previous lap was lap >0, add it to the lap list
			if self.cur_lap_number != packet.lapData[packet.header.playerCarIndex].currentLapNum and self.cur_lap_number > 0:
				self.ys.append([[], [], [], []])
				self.lap_distance_x.append([])

				last_lap_time = packet.lapData[packet.header.playerCarIndex].lastLapTime
				last_lap_time_min = math.floor(last_lap_time / 60)
				last_lap_time_s = math.floor(last_lap_time) - last_lap_time_min * 60
				last_lap_time_ms = last_lap_time % 1
				last_lap_time_string = f'Lap {self.cur_lap_number}, {last_lap_time_min}:{last_lap_time_s:02}.{last_lap_time_ms:.3f}'

				self.lap_list.addItem(last_lap_time_string)

				self.cur_lap_number = packet.lapData[packet.header.playerCarIndex].currentLapNum
		elif packet.header.packetId == 6:
			# Car telemetry data, has speed, throttle, brake, gear
			for l, attr in zip(self.ys[self.cur_lap_number], self.attrs):
				l.append(getattr(packet.carTelemetryData[packet.header.playerCarIndex], attr))

	def redraw(self):
		# Update plots data with new data, when lengths are equal
		for i in range(len(self.plots)):
			# The arrays are not guaranteed to be equal size, plot as far as the shortest of the two
			min_length = min(len(self.ys[self.cur_lap_number][i]), len(self.lap_distance_x[self.cur_lap_number]))
			if self.plots[i] is None:
				self.plots[i] = self.axes[i].plot(self.lap_distance_x[self.cur_lap_number][0:min_length],
												  self.ys[self.cur_lap_number][i][0:min_length])[0]
			else:
				self.plots[i].set_xdata(self.lap_distance_x[self.cur_lap_number][0:min_length])
				self.plots[i].set_ydata(self.ys[self.cur_lap_number][i][0:min_length])
		self.canvas.draw()

	# TODO: configs for tabs? allows for easier creation of tabs for users?
	def get_title(self):
		return 'Telemetry'
