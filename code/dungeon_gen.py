import random
from settings import *


class DungeonGenerator:
	def __init__(self, width, height, min_room_size=5, max_depth=4, corridor_width=2):
		self.width = width
		self.height = height
		self.min_room_size = min_room_size
		self.max_depth = max_depth
		self.corridor_width = corridor_width
		self.grid = [[1 for _ in range(width)] for _ in range(height)]
		self.rooms = []

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
			for dy in range(self.corridor_width):
				if 0 <= x < self.width and 0 <= y + dy < self.height:
					self.grid[y + dy][x] = 0

	def v_line(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			for dx in range(self.corridor_width):
				if 0 <= x + dx < self.width and 0 <= y < self.height:
					self.grid[y][x + dx] = 0

	def get_static_edges(self):
		# Pre-calculate and merge all wall boundaries into long segments
		h_edges = []
		v_edges = []
		
		# 1. Collect all boundary edges
		for y in range(self.height):
			for x in range(self.width):
				if self.grid[y][x] == 1:
					tile_size = TILE_SIZE
					top, bottom = y * tile_size, (y + 1) * tile_size
					left, right = x * tile_size, (x + 1) * tile_size
					
					# Boundary checks
					if y > 0 and self.grid[y-1][x] == 0: h_edges.append([left, right, top])
					if y < self.height - 1 and self.grid[y+1][x] == 0: h_edges.append([left, right, bottom])
					if x > 0 and self.grid[y][x-1] == 0: v_edges.append([top, bottom, left])
					if x < self.width - 1 and self.grid[y][x+1] == 0: v_edges.append([top, bottom, right])

		# 2. Merge horizontal edges
		merged_h = []
		h_edges.sort(key=lambda e: (e[2], e[0]))
		for e in h_edges:
			if merged_h and e[2] == merged_h[-1][2] and e[0] == merged_h[-1][1]:
				merged_h[-1][1] = e[1]
			else: merged_h.append(e)

		# 3. Merge vertical edges
		merged_v = []
		v_edges.sort(key=lambda e: (e[2], e[0]))
		for e in v_edges:
			if merged_v and e[2] == merged_v[-1][2] and e[0] == merged_v[-1][1]:
				merged_v[-1][1] = e[1]
			else: merged_v.append(e)

		# 4. Final format
		final_edges = []
		for e in merged_h: final_edges.append(((e[0], e[2]), (e[1], e[2])))
		for e in merged_v: final_edges.append(((e[2], e[0]), (e[2], e[1])))
		return final_edges

	def generate(self):
		# Initial dungeon area
		self.split_area(0, 0, self.width, self.height, 0)
		self.create_corridors()
		return self.grid


if __name__ == "__main__":
	gen = DungeonGenerator(50, 50)
	dmap = gen.generate()
	for row in dmap:
		print("".join(['#' if cell == 1 else '.' for cell in row]))
