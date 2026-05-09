from package_detection.check_for_package import BoxDimensions


class ProvidedPackageInfo:
	def __init__(self, max_box_dimensions: BoxDimensions, max_mass: float, destination: str):
		self.max_box_dimensions = max_box_dimensions
		self.max_mass = max_mass
		self.destination = destination


def get_provided_package_info(qr_code: int):
	print('Warning: get_provided_package_info() is not implemented and returns a constant value')
	return ProvidedPackageInfo(
		max_box_dimensions = BoxDimensions(0.1, 0.2, 0.15),
		max_mass = 0.5,
		destination = 'Warszawa'
	)
