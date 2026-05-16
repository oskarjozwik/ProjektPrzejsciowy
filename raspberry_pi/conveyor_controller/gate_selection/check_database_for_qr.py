from package_detection.check_for_package import BoxDimensions
import mysql.connector


class DatabaseCheckResult:
	def __init__(
		self,
		db_error: bool = False,
		entry_found: bool = True,
		max_box_dimensions: BoxDimensions = BoxDimensions(0, 0, 0),
		max_mass: float = 0,
		destination: str = ''
	):
		self.db_error = db_error
		self.entry_found = entry_found
		self.max_box_dimensions = max_box_dimensions
		self.max_mass = max_mass
		self.destination = destination


config = {
	'user': 'tapedeck',
	'password': 'Jof_159',
	'host': '192.168.0.109',
	'database': 'Tasmociag'
}


def check_database_for_qr(qr_code: int) -> DatabaseCheckResult:
	try:
		db = mysql.connector.connect(**config)
		cursor = db.cursor(dictionary = True)
		
		query = "SELECT * FROM Paczki WHERE id_paczki = %s"
		cursor.execute(query, (str(qr_code),))
		query_result = cursor.fetchone()
		
		cursor.close()
		db.close()
	except Exception as e:
		return DatabaseCheckResult(
			db_error = True
		)
	
	if not query_result:
		return DatabaseCheckResult(
			entry_found = False
		)
	
	return DatabaseCheckResult(
		max_box_dimensions = BoxDimensions(
			x = query_result['max_box_dimensions_x'],
			y = query_result['max_box_dimensions_y'],
			z = query_result['max_box_dimensions_z'],
		),
		max_mass = query_result['max_mass'],
		destination = query_result['destination']
	)