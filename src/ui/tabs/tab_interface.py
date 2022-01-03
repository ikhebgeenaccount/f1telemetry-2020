import abc

from PyQt5.QtWidgets import QTabWidget
from f1_2020_telemetry.packets import PackedLittleEndianStructure


# TODO: figure out metaclass stuff
class Tab(type(QTabWidget)):
	"""
	Defines the interface for a Tab that can be added to
	"""

	@classmethod
	def __subclasshook__(cls, subclass):
		return hasattr(subclass, 'update') and callable(subclass.update) or NotImplemented

	@abc.abstractmethod
	def update_data(self, packet: PackedLittleEndianStructure):
		raise NotImplementedError
