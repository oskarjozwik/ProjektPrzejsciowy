from package_detection.check_for_package import BoxDimensions


class DatabaseCheckResult:
	def __init__(self, entry_found: bool = True, max_box_dimensions: BoxDimensions = BoxDimensions(0,0,0), max_mass: float = 0, destination: str = ''):
		self.entry_found = entry_found
		self.max_box_dimensions = max_box_dimensions
		self.max_mass = max_mass
		self.destination = destination


def check_database_for_qr(qr_code: int) -> DatabaseCheckResult:
	print('Warning: check_database_for_qr() is not implemented and returns a constant value')
	return DatabaseCheckResult(
		max_box_dimensions = BoxDimensions(0.1, 0.2, 0.15),
		max_mass = 0.5,
		destination = 'Warszawa'
	)
