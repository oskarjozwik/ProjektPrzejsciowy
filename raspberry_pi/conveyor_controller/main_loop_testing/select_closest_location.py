"""
Generalnie to wcześniejszy kod był okej, ale nie chciałem bawić się w płatne API, a w demo nie było distanceMatrix. Też w teorii to ta funkcja jest lepsza 1 do 1, bo distanceMatrix jest do call'owania wielu tras naraz. Mierzy też po czasie, a nie po dystansie.

API key locations:
	1. the GOOGLE_MAPS_API_KEY environment variable
	2. a file named google_api_key.txt next to this script (just the key)
	3. API_KEY below
"""

import os
from concurrent.futures import ThreadPoolExecutor

import requests

PLACEHOLDER_KEY = "Enter API key here"
API_KEY = PLACEHOLDER_KEY
ENV_VAR = "GOOGLE_MAPS_API_KEY"

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
TIMEOUT_S = 10.0
MAX_PARALLEL_REQUESTS = 8


KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "google_api_key.txt")


def _clean(value: str | None) -> str:
	return (value or "").strip().strip("\"'").strip()


def find_api_key() -> tuple:
	"""Returns (key or None, description of where it came from).
	Checked in order: environment variable, google_api_key.txt, API_KEY."""
	candidates = [(f"environment variable {ENV_VAR}", os.environ.get(ENV_VAR))]
	try:
		with open(KEY_FILE, encoding = "utf-8") as f:
			candidates.append((KEY_FILE, f.read()))
	except OSError:
		pass
	candidates.append(("API_KEY in select_closest_location.py", API_KEY))

	for source, value in candidates:
		key = _clean(value)
		if key and key != PLACEHOLDER_KEY:
			return key, source
	return None, "nowhere"


def get_api_key() -> str | None:
	"""The configured key, or None if none was found."""
	return find_api_key()[0]


def _driving_time_s(key: str, origin: str, destination: str) -> float:
	"""Driving time in seconds. Raises RuntimeError with Google's message on failure."""
	response = requests.post(
		ROUTES_URL,
		headers = {
			"Content-Type": "application/json",
			"X-Goog-Api-Key": key,
			"X-Goog-FieldMask": "routes.duration",
		},
		json = {
			"origin": {"address": origin},
			"destination": {"address": destination},
			"travelMode": "DRIVE",
		},
		timeout = TIMEOUT_S,
	)
	try:
		body = response.json()
	except ValueError:
		body = {}
	if response.status_code != 200:
		message = body.get("error", {}).get("message") or response.text[:200]
		raise RuntimeError(f"HTTP {response.status_code}: {message}")

	routes = body.get("routes")
	if not routes or "duration" not in routes[0]:
		raise RuntimeError("no route found")
	return float(str(routes[0]["duration"]).rstrip("s"))   # e.g. "1238s"


def select_closest_location(target: str, available: list[str]) -> str:
	"""
	Returns the entry of `available` with the shortest driving time to `target`.
	Locations Google can't route from are skipped. Raises RuntimeError if no key
	is configured or no location could be routed (bad key, unknown target, ...).
	"""
	key = get_api_key()
	if key is None:
		raise RuntimeError(
			f"no Google API key found. Looked for: environment variable {ENV_VAR}; "
			f"file {KEY_FILE}; API_KEY in select_closest_location.py"
		)
	if not available:
		raise ValueError("no locations to choose from")

	def probe(origin: str) -> tuple:
		try:
			return origin, _driving_time_s(key, origin, target), None
		except Exception as e:
			return origin, None, str(e)

	with ThreadPoolExecutor(max_workers = min(MAX_PARALLEL_REQUESTS, len(available))) as pool:
		results = list(pool.map(probe, available))

	times: dict[str, float] = {}
	errors: list[str] = []
	for origin, seconds, error in results:
		if seconds is None:
			errors.append(f"{origin!r}: {error}")
			print(f"  route {origin!r} -> {target!r} failed: {error}")
		else:
			times[origin] = seconds

	if not times:
		raise RuntimeError(f"no route to {target!r} from any location ({'; '.join(errors)})")
	return min(times, key = times.get)
