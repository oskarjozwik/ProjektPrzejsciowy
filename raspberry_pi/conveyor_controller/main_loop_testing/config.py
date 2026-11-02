# Ustawienia hardware'u

# Camera
CAMERA_SIZE: tuple = (1920, 1080)
# Distance from camera (m) -> visible FOV width (m). Calibrate with verify_size_estimation.py.
CAMERA_FOV_MAP: dict = {
	0.175: 0.125,
	0.14: 0.08,
}

# Zmienne do CV
VAR_THRESHOLD: float = 16.0
SHADOW_THRESHOLD: float = 0.5
MIN_OBJECT_AREA_PX: int = 2000
MORPH_KERNEL: int = 11

# Robienie zdjęcia QR / do update'u jak będzie automatyczne spychanie
SETTLE_TIME_S: float = 2.0
BG_REFERENCE_FRAMES: int = 60

# Czujnik dystansu
TRIGGER_PIN: int = 23
ECHO_PIN: int = 24
MAX_DISTANCE_M: float = 1.0
DISTANCE_SAMPLES: int = 5

# Tensometr 
NAU7802_ADDRESS: int = 0x2A
LOAD_CELL_SAMPLES: int = 10
TARE_SAMPLES: int = 40
LOAD_CELL_COUNTS_PER_GRAM: float = 4028

# PLC / Modbus 
PLC_IP: str = "10.0.0.10"
PLC_PORT: int = 502
DEVICE_ID: int = 255
REG_GATE: int = 12               # MI12
COIL_PACKAGE_ARRIVED: int = 0    # MB0
PACKAGE_CLEAR_TIMEOUT_S: float = 30.0

# SQL 
SQL_CONFIG: dict = {
	"user": "tapedeck",
	"password": "Jof_159",   # TODO: move to an environment variable
	"host": "100.67.47.107",
	"database": "TestZlozenia",
}

# Inne 
CAPTURE_PERIOD_S: float = 2.0
SETTLE_BEFORE_MEASURE_S: float = 2.0
ERROR_GATE: int = 0
GATE_CONFIG_PATH: str = "gates.txt" # tu są przechowywane informacje o konfiguracji bramek
