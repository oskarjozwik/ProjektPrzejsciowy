import googlemaps
from googlemaps.distance_matrix import distance_matrix

api_key = 'Enter API key here'
client = googlemaps.Client(key = api_key)

def select_closest_location(
	target: str,
	available: list[str]
) -> str:
	print('Warning: select_closest_location() needs a Google Maps API key to work properly')
	
	matrix = googlemaps.distance_matrix.distance_matrix(
		client = client,
		origins = available,
		destinations = [target],
		mode = 'driving'
	)
	
	distances = []
	for row in matrix['rows']:
		distances.append(row['elements'][0]['duration']['value'])
	closest_location = available[distances.index(min(distances))]
	
	return closest_location