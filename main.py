import os
import sys
from os.path import abspath

import numpy as np
from PyQt5 import QtWidgets
from matplotlib import pyplot as plt, cm
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection

from src import sessions
from src.ui.app_window import AppWindow


def plot_data(data_path):
	sd = sessions.SessionData(3737230889795252704, data_path)  # RB ring
	# sd = sessions.SessionData(9607873297504516202, data_path)  # Silverstone
	# sd = sessions.SessionData(11541244035795733387, data_path)  # Brazil

	field_to_plot = 'engineRPM'

	data = sd.load_telemetry(lap_number=4)
	print(data[field_to_plot])
	vmax = max(data[field_to_plot])

	fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, sharex='all')

	ax0.plot(data['lapDistance'], data['speed'])
	ax1.plot(data['lapDistance'], data['throttle'])
	ax2.plot(data['lapDistance'], data['brake'])
	ax3.plot(data['lapDistance'], data['gear'])

	fig, ax = plt.subplots()

	x = np.array(data['worldPositionX'])
	y = np.array(data['worldPositionZ'])

	points = np.array([x, y]).T.reshape(-1, 1, 2)
	segments = np.concatenate([points[:-1], points[1:]], axis=1)

	cmap = cm.get_cmap('viridis', int(vmax))
	lc_comp = LineCollection(segments, cmap=cmap, norm=plt.Normalize(1, vmax))
	lc_comp.set_array(data[field_to_plot])
	lc_comp.set_linewidth(5)

	ax.add_collection(lc_comp)
	ax.axis('equal')
	# For some reason, tracks are mirroed so unmirror it by inverting an axis
	ax.invert_yaxis()
	ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

	sm = ScalarMappable(cmap=cmap, norm=plt.Normalize(1, cmap.N + 1))
	fig.colorbar(sm)

	plt.show()


if __name__ == '__main__':
	# TODO: create config for save path
	data_root = abspath(os.getcwd())

	# --record is to record data while playing F1 2020
	if '--record' in sys.argv:
		app = QtWidgets.QApplication(sys.argv)
		window = AppWindow(data_root)

		# Start qt application
		app.exec_()
	elif '--plot' in sys.argv:
		plot_data(os.path.join(data_root, 'data'))
