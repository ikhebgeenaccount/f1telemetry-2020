import configparser
import logging
import os.path
import socket

import matplotlib
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import QWidget, QTabWidget
from f1_2020_telemetry.packets import PackedLittleEndianStructure, unpack_udp_packet

from src import packets

from src.ui.tabs import *

matplotlib.use('Qt5Agg')


class AppWindow(QtWidgets.QMainWindow):
	"""
	AppWindow is the main window of the application.
	It has a TabsWidget to which tabs from ui.tabs are added.
	Which tabs are added depends on the session type and is specified in cfg/ui.ini
	"""

	def __init__(self, data_root, *args, **kwargs):
		"""
		Create an AppWindow.
		:param data_root: Points to the base folder which contains the folders data, cfg and logs.
		:param args:
		:param kwargs:
		"""
		super(AppWindow, self).__init__(*args, **kwargs)
		logging.info('Initializing AppWindow')

		self.title = 'F1 2020 telemetry tool'
		self.setWindowTitle(self.title)

		# Create Worker to listen for incoming packets
		self.packet_listener = PacketListener(data_root)

		# Create QThread on which packet_listener will run
		self.l_thread = QThread()
		self.packet_listener.moveToThread(self.l_thread)

		# When the thread is started, run packet_listener.listen
		self.l_thread.started.connect(self.packet_listener.listen)
		self.packet_listener.received.connect(self.update_data)
		self.l_thread.start()

		# Create widget with tabs
		self.tabs_widget = TabsWidget(data_root)
		self.setCentralWidget(self.tabs_widget)

		# Show this window
		self.showMaximized()

	@pyqtSlot(PackedLittleEndianStructure)
	def update_data(self, packet):
		"""
		Updates the AppWindow with the new data from packet.
		:param packet: UPD telemetry packet from the F1 game.
		:return:
		"""
		self.tabs_widget.update_data(packet)


class TabsWidget(QTabWidget):

	def __init__(self, data_root):
		super().__init__()

		self.data_root = data_root

		# Read UI config
		self.ui_config = configparser.ConfigParser()
		self.ui_config.read(os.path.join(data_root, 'cfg', 'ui.ini'))

		self.session_type = -1

		# Timer for refreshing of active tab
		self.timer = QTimer()
		self.timer.setInterval(int(self.ui_config['general']['refresh_rate']))
		self.timer.timeout.connect(self.redraw_active_tab)
		self.timer.start()

		# Called when the currently displayed tab changes
		self.currentChanged.connect(self.tab_changed)

	def update_data(self, packet):
		# TODO: check for event session ended for post screen

		# If it's a session packet, set the session type of the TabsWidget
		if packet.header.packetId == 1:
			if packet.sessionType != self.session_type:
				self.session_type = packet.sessionType

				# TODO: remove tabs
				# TODO: use config
				# # Update tabs according to UI config
				# tab_classes_names = self.ui_config[str(self.session_type]['tabs'].split(',')
				#
				# for t in tab_classes_names:
				# 	print(eval(t))  # TODO: maybe need to do f'src.ui.tabs.{t}' ?

				t = TelemetryTab()

				self.addTab(t, t.get_title())

				print('tab added')

		# Pass the new packet to each tab
		for i in range(0, self.count()):
			self.widget(i).update_data(packet)

	@pyqtSlot(int)
	def tab_changed(self, new_index):
		self.widget(new_index).redraw()

	@pyqtSlot()
	def redraw_active_tab(self):
		if self.count() > 0:
			self.currentWidget().redraw()


class PacketListener(QObject):
	"""
	PacketListener is a Worker class that listens for F1 2020 UDP packets.
	"""
	received = pyqtSignal(PackedLittleEndianStructure)

	def __init__(self, data_root):
		super().__init__()
		self.data_root = data_root
		self.quit_flag = False

	def listen(self):
		udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		udp_socket.bind(("", 20777))

		# Initial session is whatever
		curr_session_uid = 0
		packet_saver = None

		while not self.quit_flag:
			udp_packet = udp_socket.recv(2048)
			packet = unpack_udp_packet(udp_packet)

			if curr_session_uid != packet.header.sessionUID:
				print(f'Creating new session stuff with sessionUID {packet.header.sessionUID}\n and packet {packet}')
				# Sets logging up and points it to save_path/logs/[sessionUID].log
				logging.basicConfig(filename=os.path.join(self.data_root, 'logs', f'{packet.header.sessionUID}.log'), level=logging.DEBUG,
									format='%(asctime)s %(levelname)-8s %(module)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
				packet_saver = packets.PacketSaver(packet.header.sessionUID, self.data_root)

			# Save this sessionUID to be able to check if new one has started
			curr_session_uid = packet.header.sessionUID

			# Save the packet
			packet_saver.save(packet)
			# Emit the packet to GUI
			self.received.emit(packet)

	@pyqtSlot()
	def quit(self):
		self.quit_flag = True
