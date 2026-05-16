from check_database_for_qr import check_database_for_qr
from package_detection.check_for_package import BoxDimensions
from select_closest_location import select_closest_location


class GateSelectionResult:
	def __init__(self, gate: int = -1, info: str = ''):
		self.gate = gate
		self.info = info


def select_gate_for_package(
	mass: float,
	box_dimensions: BoxDimensions,
	qr_code: int,
	gate_destinations: list[str],
) -> GateSelectionResult:
	database_check_result = check_database_for_qr(qr_code)
	
	if database_check_result.db_error:
		return GateSelectionResult(
			info = 'db_error'
		)
	if not database_check_result.entry_found:
		return GateSelectionResult(
			info = 'entry_not_found'
		)
	if mass > database_check_result.max_mass:
		return GateSelectionResult(
			info = 'max_mass_exceeded'
		)
	if box_dimensions.x > database_check_result.max_box_dimensions.x or box_dimensions.y > database_check_result.max_box_dimensions.y or box_dimensions.z > database_check_result.max_box_dimensions.z:
		return GateSelectionResult(
			info = 'max_dimensions_exceeded'
		)
	
	closest_location = select_closest_location(
		target = database_check_result.destination,
		available = gate_destinations,
	)
	return GateSelectionResult(
		gate = gate_destinations.index(closest_location),
		info = closest_location
	)
