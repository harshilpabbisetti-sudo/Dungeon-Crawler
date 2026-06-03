import random


class DungeonGenerator:
	def __init__(self, width, height, min_room_size=5, max_depth=4):
		self.width = width
		self.height = height
		self.min_room_size = min_room_size
		self.max_depth = max_depth
		self.grid = [[1 for _ in range(width)] for _ in range(height)]
		self.rooms = []

	def generate(self):
		# Initial dungeon area
		self.split_area(0, 0, self.width, self.height, 0)
		self.create_corridors()
		return self.grid

	def split_area(self, x, y, w, h, depth):
		# Stop splitting if max depth reached or area too small for a room plus padding
		if depth >= self.max_depth or w < self.min_room_size + 4 or h < self.min_room_size + 4:
			self.create_room(x, y, w, h)
			return

		# Determine split direction: horizontal or vertical
		split_horizontally = random.choice([True, False])
		if w > h * 1.25:
			split_horizontally = False
		elif h > w * 1.25:
			split_horizontally = True

		if split_horizontally:
			# Horizontal split
			if h < (self.min_room_size + 2) * 2:
				self.create_room(x, y, w, h)
				return
			
			split_point = random.randint(self.min_room_size + 2, h - (self.min_room_size + 2))
			self.split_area(x, y, w, split_point, depth + 1)
			self.split_area(x, y + split_point, w, h - split_point, depth + 1)
		else:
			# Vertical split
			if w < (self.min_room_size + 2) * 2:
				self.create_room(x, y, w, h)
				return
			
			split_point = random.randint(self.min_room_size + 2, w - (self.min_room_size + 2))
			self.split_area(x, y, split_point, h, depth + 1)
			self.split_area(x + split_point, y, w - split_point, h, depth + 1)

	def create_room(self, x, y, w, h):
		# Ensure we have at least min_room_size space
		# If w-2 is less than min_room_size, we use the available space minus padding
		max_w = max(self.min_room_size, w - 2)
		max_h = max(self.min_room_size, h - 2)
		
		room_w = random.randint(self.min_room_size, max_w)
		room_h = random.randint(self.min_room_size, max_h)
		
		# Ensure room fits in the area
		room_x = x + random.randint(1, max(1, w - room_w - 1))
		room_y = y + random.randint(1, max(1, h - room_h - 1))

		# Carve room into grid (0 = Floor)
		for i in range(room_y, min(room_y + room_h, self.height - 1)):
			for j in range(room_x, min(room_x + room_w, self.width - 1)):
				self.grid[i][j] = 0
		
		self.rooms.append({'x': room_x, 'y': room_y, 'w': room_w, 'h': room_h, 'center': (room_x + room_w // 2, room_y + room_h // 2)})

	def create_corridors(self):
		# Connect rooms in sequence
		for i in range(len(self.rooms) - 1):
			start_x, start_y = self.rooms[i]['center']
			end_x, end_y = self.rooms[i+1]['center']

			# Create L-shaped corridor
			if random.choice([True, False]):
				# Move horizontally then vertically
				self.h_line(start_x, end_x, start_y)
				self.v_line(start_y, end_y, end_x)
			else:
				# Move vertically then horizontally
				self.v_line(start_y, end_y, start_x)
				self.h_line(start_x, end_x, end_y)

	def h_line(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			if 0 <= x < self.width and 0 <= y < self.height:
				self.grid[y][x] = 0

	def v_line(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			if 0 <= x < self.width and 0 <= y < self.height:
				self.grid[y][x] = 0


if __name__ == "__main__":
	gen = DungeonGenerator(50, 50)
	dmap = gen.generate()
	for row in dmap:
		print("".join(['#' if cell == 1 else '.' for cell in row]))
