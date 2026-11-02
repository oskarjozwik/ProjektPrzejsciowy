import config


def load_gate_config(path: str = config.GATE_CONFIG_PATH) -> dict[int, str]:
	# Zaczytanie config.py, nie czyta komentarzy, nie pozwala na nadpisanie bramki 0 (error gate)
	gates: dict[int, str] = {}
	try:
		with open(path, encoding = "utf-8") as f:
			for line_no, line in enumerate(f, start = 1):
				line = line.split("#", 1)[0].strip()
				if not line:
					continue
				num, sep, location = line.partition("=")
				if not sep or not num.strip().isdigit() or not location.strip():
					print(f"  gate config line {line_no} ignored: {line!r}")
					continue
				gate = int(num)
				if gate == config.ERROR_GATE:
					print(f"  gate config line {line_no} ignored: gate {config.ERROR_GATE} is reserved")
					continue
				gates[gate] = location.strip()
	except OSError as e:
		print(f"  cannot read gate config {path!r}: {e}")
	return gates


def select_gate_for_destination(destination: str, gates: dict[int, str]) -> int:
	"""Gate whose location is closest to the package's destination."""
	if not gates:
		print("  no gates configured")
		return config.ERROR_GATE

	# Imported lazily so a missing `requests` package only affects lookups,
	# not the whole application.
	try:
		from select_closest_location import select_closest_location
		closest = select_closest_location(target = destination, available = list(gates.values()))
	except Exception as e:
		print(f"  closest-location lookup failed: {e}")
		return config.ERROR_GATE

	for gate, location in gates.items():
		if location == closest:
			return gate
	return config.ERROR_GATE
