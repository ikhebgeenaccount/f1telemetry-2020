team_ids = {}
driver_ids = {}
track_ids = {}
nationalities_ids = {}


def load_ids():
	"""
	Loads the ids and corresponding names of tracks, teams, drivers and nationalities into their corresponding dicts.
	:return:
	"""
	for d, f in zip([team_ids, driver_ids, track_ids, nationalities_ids], ['ids/teams.id', 'ids/drivers.id', 'ids/tracks.id', 'ids/nationalities.id']):
		with open(f, encoding='UTF-8') as d_file:
			for line in d_file:
				id, name = line.split(',')
				d[int(id)] = name.strip()