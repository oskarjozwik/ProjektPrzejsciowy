class Category:
	def __init__(self, name: str = '???', max_mass: float = 0, max_x: float = 0, max_y: float = 0, max_z: float = 0):
		self.name = name
		self.max_mass = max_mass
		self.max_x = max_x
		self.max_y = max_y
		self.max_z = max_z

def get_categories() -> list[Category]:
	categories = []
	try:
		with open('categories.txt', 'r') as file:
			next(file)
			for line in file:
				parts = line.strip().split()
				if len(parts) == 5:
					categories.append(
						Category(
							name = parts[0],
							max_mass = float(parts[1]),
							max_x = float(parts[2]),
							max_y = float(parts[3]),
							max_z = float(parts[4]),
						)
					)
	except FileNotFoundError:
		categories = [Category()]
	return categories