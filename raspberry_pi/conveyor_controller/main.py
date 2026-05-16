import cv2 as cv

from has_package_just_arrived import has_package_just_arrived
from package_detection.check_for_package import check_for_package
from transport_package_to_gate import transport_package_to_gate
from gate_selection.select_gate_for_package import select_gate_for_package

gate_destinations: list[str] = [
	"Poznań", "Warszawa",
]

def main():
	is_conveyor_empty: bool = True
	
	while cv.waitKey( 10 ) != ord( 'q' ):
		if is_conveyor_empty:
			package_check_result = check_for_package()
			package_check_result.print()
			
			if package_check_result.box_detected and package_check_result.qr_detected:
				is_conveyor_empty = False
				
				gate_selection_result = select_gate_for_package(
					mass = package_check_result.mass,
					box_dimensions = package_check_result.box_dimensions,
					qr_code = package_check_result.qr_code,
					gate_destinations = gate_destinations,
				)
				print(gate_selection_result.info)
				transport_package_to_gate( gate_selection_result.gate )
		else:
			if has_package_just_arrived():
				is_conveyor_empty = True

if __name__ == "__main__":
	main()
