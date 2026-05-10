from check_database_for_qr import check_database_for_qr
from package_detection.check_for_package import BoxDimensions
from select_closest_location import select_closest_location

def select_gate_for_package(
	mass: float,
	box_dimensions: BoxDimensions,
	qr_code: int,
	gate_destinations: list[str],
) -> int:
	database_check_result = check_database_for_qr( qr_code )
	
	if not database_check_result.entry_found:
		return -1
	if mass > database_check_result.max_mass:
		return -1
	if box_dimensions.x > database_check_result.max_box_dimensions.x or box_dimensions.y > database_check_result.max_box_dimensions.y or box_dimensions.z > database_check_result.max_box_dimensions.z:
		return -1
	
	closest_location = select_closest_location(
		target = database_check_result.destination,
		available = gate_destinations,
	)
	return gate_destinations.index( closest_location )
