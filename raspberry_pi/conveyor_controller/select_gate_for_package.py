from package_detection.check_for_package import BoxDimensions
from select_closest_location import select_closest_location


def select_gate_for_package(
	mass: float,
	box_dimensions: BoxDimensions,
	max_mass: float,
	max_box_dimensions: BoxDimensions,
	destination: str,
	gate_destinations: list[str]
) -> int:
	if mass > max_mass:
		return -1
	if box_dimensions.x > max_box_dimensions.x or box_dimensions.y > max_box_dimensions.y or box_dimensions.z > max_box_dimensions.z:
		return -1

	closest_location = select_closest_location(
		target = destination,
		available = gate_destinations
	)
	return gate_destinations.index(closest_location)