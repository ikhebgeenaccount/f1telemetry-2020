import configparser
import logging
import os.path
import socket

import matplotlib
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget
from f1_2020_telemetry.packets import PackedLittleEndianStructure, unpack_udp_packet

from src import packets

# from src.ui.tabs import *

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
		self.show()

	@pyqtSlot(PackedLittleEndianStructure)
	def update_data(self, packet):
		"""
		Updates the AppWindow with the new data from packet.
		:param packet: UPD telemetry packet from the F1 game.
		:return:
		"""
		self.tabs_widget.update_data(packet)

		print('update')


class TabsWidget(QWidget):

	def __init__(self, data_root):
		super().__init__()

		self.data_root = data_root

		# Read UI config
		self.ui_config = configparser.ConfigParser()
		self.ui_config.read(os.path.join(data_root, 'cfg', 'ui.ini'))

		self.session_type = -1

	def update_data(self, packet):
		# If it's a sessino packet, set the session type of the TabsWidget
		if packet.header.packetId == 1:
			if packet.sessionType != self.session_type:
				self.session_type = packet.sessionType

				# Update tabs according to UI config
				tab_classes = self.ui_config['tabs'][str(self.session_type)].split(',')

				for t in tab_classes:  # TODO: maybe need to do f'tabs.{t}' ?
					print(eval(t))


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

				self.received.emit(packet)

			# Save this sessionUID to be able to check if new one has started
			curr_session_uid = packet.header.sessionUID

			# Save the packet
			packet_saver.save(packet)
