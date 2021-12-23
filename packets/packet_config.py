import configparser


class PacketConfig():
	"""
	PacketConfig reads a .ini file that specifies which fields should be saved per packet type, or per nested data field.
	"""

	def __init__(self, file_path):
		"""
		Creates a PacketConfig from the file at file_path.
		:param file_path:
		"""
		self._packet_config = {}

		# Loads config of what fields to save
		cfg_parser = configparser.ConfigParser()
		cfg_parser.read(file_path)

		cfg_parser['nested data']['lap_data'].split(',')

		dict_cfgp = dict(cfg_parser)
		for section in ['packets', 'nested data']:
			for key in dict_cfgp[section]:
				self._packet_config[key] = {}
				self._packet_config[key]['list'] = dict_cfgp[section][key].split(',')
				self._packet_config[key]['string'] = dict_cfgp[section][key]

	def get_fields(self, name, list_format=True):
		"""
		Returns the fields that need to be saved for data structure 'name', name can be one of the keys in packet_keys.ini
		Returns the fields in one string, separated by commas (',') or a list split by those commas.
		:param name: Name of data structure
		:param list_format: Specifies format of return, True to return a list, False to return a string
		:return:
		"""
		if list_format:
			return self._packet_config[name]['list']
		else:
			return self._packet_config[name]['string']
