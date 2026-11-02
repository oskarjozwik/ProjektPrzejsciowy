import mysql.connector

import config

_conn = None


def connect() -> None:
	global _conn
	_conn = mysql.connector.connect(**config.SQL_CONFIG)
	# Autocommit odświeża informacje (bez mamy tylko info z pierwszego reada)
	_conn.autocommit = True


def close() -> None:
	try:
		_conn.close()
	except Exception:
		pass


def fetch_package(qr_id: int) -> dict | None:
	if not _conn.is_connected():
		_conn.reconnect(attempts = 3, delay = 1)
	cursor = _conn.cursor(dictionary = True)
	try:
		cursor.execute(
			"SELECT max_weight, max_x, max_y, max_z, origin, destination "
			"FROM Paczki WHERE qr_id = %s",
			(qr_id,),
		)
		row = cursor.fetchone()
	finally:
		cursor.close()
	if row is None:
		return None
	for key in ("max_x", "max_y", "max_z"):
		row[key] = float(row[key]) / 1000.0
	return row
