from pymodbus.client import ModbusTcpClient

PLC_IP = "10.0.0.10" # tym razem jest ustawione na sztywno, IP ethernetowe PI to 10.0.0.11
PLC_PORT = 502
DEVICE_ID = 255
client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

if client.connect():
    print("PLC connected")
else:
    print("PLC connection failed")
    exit()

# Pisanie bitow
client.write_coil(0,True, device_id=DEVICE_ID) # napisanie jednego bita do MB0
MB0 = client.read_coils(0, count=1, device_id=DEVICE_ID)
print(f"MB0 = {MB0.bits[0]}") # mimo, że bity to zwraca cały pakiet ITP 8-bitowy xdd wiec trzxeba go przyciac

# Pisanie intow
client.write_register(0, 69, device_id=DEVICE_ID) # napisanie 69 do MI0
MI0 = client.read_holding_registers(0, count=1, device_id=DEVICE_ID)
print(f"MI0 = {MI0.registers[0]}") # podobna sytuacja jak wczesniej
