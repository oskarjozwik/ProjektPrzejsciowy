import cv2 as cv

from get_provided_package_info import get_provided_package_info
from package_detection.check_for_package import check_for_package
from package_just_moved import package_just_moved
from request_just_completed import request_just_completed
from request_transport_to_gate import request_transport_to_gate
from select_gate_for_package import select_gate_for_package

gate_destinations: list[str] = [
	"Poznań", "Warszawa"
]


def main():
	package_detected_on_scale: bool = False
	requested_gate: int = -1
	busy_with_previous_request: bool = False
	new_request: bool = False
	
	while cv.waitKey(10) != ord('q'):
		if package_detected_on_scale:
			if package_just_moved():
				package_detected_on_scale = False
				continue
			
			if new_request:
				if busy_with_previous_request:
					if request_just_completed():
						busy_with_previous_request = False
					else:
						continue
				
				request_transport_to_gate(requested_gate)
				new_request = False
				busy_with_previous_request = True
		else:
			package_check_result = check_for_package()
			package_check_result.print()
			
			if package_check_result.box_detected and package_check_result.qr_detected:
				package_detected_on_scale = True
				
				provided_package_info = get_provided_package_info(package_check_result.qr_code)
				requested_gate = select_gate_for_package(
					mass = package_check_result.mass,
					box_dimensions = package_check_result.box_dimensions,
					max_mass = provided_package_info.max_mass,
					max_box_dimensions = provided_package_info.max_box_dimensions,
					destination = provided_package_info.destination,
					gate_destinations = gate_destinations
				)
				new_request = True


if __name__ == "__main__":
	main()
