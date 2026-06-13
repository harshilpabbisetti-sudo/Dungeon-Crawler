import heapq

class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Estimated cost from current node to end
        self.f = 0  # Total cost (g + h)

    def __lt__(self, other):
        return self.f < other.f

def get_path(grid, start, end):
    
    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])
    
    open_list = []
    closed_set = set()
    
    heapq.heappush(open_list, start_node)
    
    while open_list:
        current_node = heapq.heappop(open_list)
        closed_set.add((current_node.x, current_node.y))
        
        # Found the goal
        if (current_node.x, current_node.y) == (end_node.x, end_node.y):
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            if len(path)<20:
                return path[::-1] # Return reversed path
            else: return None
            
        # Neighbors (8-way: Orthogonal and Diagonal)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = current_node.x + dx, current_node.y + dy
            
            # Check bounds and walls
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
                # Prevent clipping through corners
                if dx != 0 and dy != 0:
                    if grid[current_node.y][nx] != 0 or grid[ny][current_node.x] != 0:
                        continue

                if (nx, ny) in closed_set:
                    continue
                    
                neighbor = Node(nx, ny, current_node)
                
                # Movement cost: 1 for orthogonal, ~1.414 for diagonal
                move_cost = 1.414 if (dx != 0 and dy != 0) else 1
                neighbor.g = current_node.g + move_cost
                
                # Octile distance heuristic for 8-way movement
                h_dx = abs(neighbor.x - end_node.x)
                h_dy = abs(neighbor.y - end_node.y)
                neighbor.h = max(h_dx, h_dy) + (1.414 - 1) * min(h_dx, h_dy)
                
                neighbor.f = neighbor.g + neighbor.h
                
                # Check if this node is already in open list with a lower cost
                if any(node.x == nx and node.y == ny and node.g <= neighbor.g for node in open_list):
                    continue
                    
                heapq.heappush(open_list, neighbor)
                
    return None # No path found
