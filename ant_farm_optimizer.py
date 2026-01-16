import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import random

class AntFarm:
    def __init__(self, grid_size=(50, 50), cart_size=None):
        self.grid_size = grid_size
        self.pheromone = np.ones(grid_size) * 0.1
        self.obstacles = np.zeros(grid_size, dtype=bool)
        self.start = None
        self.ends = []
        self.ants = []
        self.best_paths = {}
        self.best_path_lengths = {}
        self.num_ants = 50 # this number sets the accuracy of the test
        self.evaporation_rate = 0.1
        self.pheromone_deposit = 100
        self.alpha = 1.0
        self.beta = 2.0
        self.sequential = True # set to True to have the ants visits enpoints in order.
        self.return_to_start = True #set to True to return to start point.
        self.best_route = None
        self.best_route_length = float('inf')

        # cart dimensions (height, width) for collision detection
        self.cart_size = cart_size if cart_size else (1, 1)
        self.traffic_heatmap = np.zeros(grid_size, dtype=int)
        self.bottlenecks = []
        self.all_routes = []

        # separate pheromones and best paths for people vs thicc bois
        self.pheromone_people = np.ones(grid_size) * 0.1
        self.pheromone_carts = np.ones(grid_size) * 0.1
        self.best_route_people = None
        self.best_route_carts = None
        self.best_route_length_people = float('inf')
        self.best_route_length_carts = float('inf')
        self.all_routes_people = []
        self.all_routes_carts = []
    
    # sets single start point and one or more end points
    def set_start_end(self, start, end, sequential=False, return_to_start=False):
        self.start = start
        self.sequential = sequential
        self.return_to_start = return_to_start
        
        if isinstance(end, list):
            self.ends = end
        else:
            self.ends = [end]
        
        if not sequential:
            for e in self.ends:
                self.best_paths[e] = None
                self.best_path_lengths[e] = float('inf')
    
    # adds rectangular obstacle to the grid
    def add_obstacle(self, top_left, bottom_right):
        y1, x1 = top_left
        y2, x2 = bottom_right
        self.obstacles[y1:y2, x1:x2] = True
    
    # loads layout from array where 0 = free, 1 = obstacle, 2 = start, 3 = ends
    def load_custom_layout(self, layout_array):
        self.obstacles = (layout_array == 1)
        start_pos = np.where(layout_array == 2)
        
        if len(start_pos[0]) > 0:
            self.start = (start_pos[0][0], start_pos[1][0])
        
        self.ends = []
        for val in range(3, 10):
            end_pos = np.where(layout_array == val)
            if len(end_pos[0]) > 0:
                for i in range(len(end_pos[0])):
                    self.ends.append((end_pos[0][i], end_pos[1][i]))
        
        if not self.sequential:
            for e in self.ends:
                self.best_paths[e] = None
                self.best_path_lengths[e] = float('inf')
    
    # checks if cart at position would collide with obstacles
    def check_cart_collision(self, pos):
        y, x = pos
        cart_h, cart_w = self.cart_size

        # check if cart footprint extends beyond grid
        if (y + cart_h > self.grid_size[0] or
            x + cart_w > self.grid_size[1]):
            return True

        # check if any part of cart overlaps with obstacle
        cart_footprint = self.obstacles[y:y+cart_h, x:x+cart_w]
        return np.any(cart_footprint)

    # returns valid neighboring positions including diagonals
    def get_neighbors(self, pos, check_cart=True):
        y, x = pos
        nbrs = []
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if (0 <= ny < self.grid_size[0] and
                0 <= nx < self.grid_size[1] and
                not self.obstacles[ny, nx]):
                if check_cart:
                    if not self.check_cart_collision((ny, nx)):
                        nbrs.append((ny, nx))
                else:
                    nbrs.append((ny, nx))
        return nbrs

    # calculates movement probability to each neighbor based on pheromone and distance heuristic
    def calculate_probability(self, current, nbrs, visited, target, pheromone_map=None):
        probs = []
        if pheromone_map is None:
            pheromone_map = self.pheromone

        for nbr in nbrs:
            if nbr in visited:
                probs.append(0)
                continue

            pher = pheromone_map[nbr] ** self.alpha
            dist = np.sqrt((nbr[0] - target[0])**2 + (nbr[1] - target[1])**2)
            heur = (1.0 / (dist + 1)) ** self.beta
            probs.append(pher * heur)

        total = sum(probs)
        if total == 0:
            return [1/len(nbrs)] * len(nbrs) if nbrs else []
        return [p/total for p in probs]
    
    # executes single ant pathfinding to specified target endpoint
    def run_ant(self, target):
        path = [self.start]
        visited = set([self.start])
        curr = self.start
        max_steps = self.grid_size[0] * self.grid_size[1]
        
        for _ in range(max_steps):
            if curr == target:
                return path
            
            nbrs = self.get_neighbors(curr)
            if not nbrs:
                break
            
            probs = self.calculate_probability(curr, nbrs, visited, target)
            
            if sum(probs) == 0:
                break
            
            next_pos = random.choices(nbrs, weights=probs)[0]
            path.append(next_pos)
            visited.add(next_pos)
            curr = next_pos
        
        return None
    
    # executes single ant through sequential route visiting all endpoints in order
    def run_ant_sequential(self, start_pos, targets, check_cart=True, pheromone_map=None):
        full_route = []
        curr_start = start_pos

        for target in targets:
            path = [curr_start]
            visited = set([curr_start])
            curr = curr_start
            max_steps = self.grid_size[0] * self.grid_size[1]

            for _ in range(max_steps):
                if curr == target:
                    if len(full_route) > 0:
                        path = path[1:]
                    full_route.extend(path)
                    curr_start = target
                    break

                nbrs = self.get_neighbors(curr, check_cart=check_cart)
                if not nbrs:
                    return None

                probs = self.calculate_probability(curr, nbrs, visited, target, pheromone_map=pheromone_map)

                if sum(probs) == 0:
                    return None

                next_pos = random.choices(nbrs, weights=probs)[0]
                path.append(next_pos)
                visited.add(next_pos)
                curr = next_pos
            else:
                return None

        return full_route if full_route else None
    
    # applies pheromone evaporation and deposits new pheromones from successful paths
    def update_pheromones(self, paths_by_target):
        self.pheromone *= (1 - self.evaporation_rate)
        self.pheromone = np.maximum(self.pheromone, 0.1)
        
        for target, paths in paths_by_target.items():
            for path in paths:
                if path:
                    deposit = self.pheromone_deposit / len(path)
                    for pos in path:
                        self.pheromone[pos] += deposit
                    
                    if len(path) < self.best_path_lengths[target]:
                        self.best_path_lengths[target] = len(path)
                        self.best_paths[target] = path
    
    # applies pheromone evaporation and deposits for sequential routes
    def update_pheromones_sequential(self, routes):
        self.pheromone *= (1 - self.evaporation_rate)
        self.pheromone = np.maximum(self.pheromone, 0.1)

        for route in routes:
            if route:
                # routes for traffic analysis
                self.all_routes.append(route)

                deposit = self.pheromone_deposit / len(route)
                for pos in route:
                    self.pheromone[pos] += deposit
                    # track traffic through each cell
                    self.traffic_heatmap[pos] += 1

                if len(route) < self.best_route_length:
                    self.best_route_length = len(route)
                    self.best_route = route
    
    # detects bottlenecks where paths narrow and traffic concentrates
    def detect_bottlenecks(self, threshold=None):
        if threshold is None:
            threshold = len(self.all_routes) * 0.3

        self.bottlenecks = []

        # find cells with high traffic
        high_traffic = np.where(self.traffic_heatmap > threshold)

        for i in range(len(high_traffic[0])):
            y, x = high_traffic[0][i], high_traffic[1][i]

            # count passable neighbors
            cart_h, cart_w = self.cart_size
            neighbors = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < self.grid_size[0] and
                        0 <= nx < self.grid_size[1] and
                        not self.obstacles[ny, nx] and
                        not self.check_cart_collision((ny, nx))):
                        neighbors += 1

            # bottleneck if high traffic + few neighbors
            if neighbors <= 4:
                self.bottlenecks.append({
                    'position': (y, x),
                    'traffic_count': int(self.traffic_heatmap[y, x]),
                    'clearance': neighbors
                })

        return self.bottlenecks

    # analyzes route conflicts where multiple carts use same cells
    def analyze_route_conflicts(self, time_window=10):
        conflicts = []

        # simulate carts moving along their routes simultaneously
        for t in range(time_window):
            occupied = {}

            for route_idx, route in enumerate(self.all_routes[-20:]):
                if t < len(route):
                    pos = route[t]

                    # check cart footprint at this position
                    cart_h, cart_w = self.cart_size
                    for dy in range(cart_h):
                        for dx in range(cart_w):
                            cell = (pos[0] + dy, pos[1] + dx)
                            if cell in occupied:
                                conflicts.append({
                                    'time': t,
                                    'position': cell,
                                    'routes': [occupied[cell], route_idx]
                                })
                            else:
                                occupied[cell] = route_idx

        return conflicts

    # executes one complete iteration of ant colony optimization for all endpoints
    def run_iteration(self):
        if self.sequential:
            routes = []
            targets = self.ends.copy()
            if self.return_to_start:
                targets.append(self.start)

            for _ in range(self.num_ants):
                route = self.run_ant_sequential(self.start, targets)
                routes.append(route)

            self.update_pheromones_sequential(routes)
            return routes
        else:
            paths_by_target = {e: [] for e in self.ends}

            for target in self.ends:
                for _ in range(self.num_ants):
                    path = self.run_ant(target)
                    paths_by_target[target].append(path)
                    if path:
                        self.all_routes.append(path)
                        for pos in path:
                            self.traffic_heatmap[pos] += 1

            self.update_pheromones(paths_by_target)
            return paths_by_target


# creates sample production floor layout with multiple endpoints
def create_template_layout():
    farm = AntFarm(grid_size=(40, 60))
    
    # parallel mode: find paths to all endpoints independently
    # farm.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)])
    
    # sequential mode: visit endpoints in order (1->2->3), optionally return to start
    farm.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)], 
                       sequential=True, return_to_start=False)
    
    farm.add_obstacle((8, 10), (12, 30))
    farm.add_obstacle((20, 10), (24, 30))
    farm.add_obstacle((8, 35), (24, 45))
    farm.add_obstacle((28, 15), (32, 25))
    farm.add_obstacle((15, 48), (19, 58))
    
    return farm


# visualizes ant colony optimization with animated pathfinding
def visualize_ant_farm(farm, iterations=100): # change interations to add or shorten tests
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    iter_count = [0]
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
    
    def update(frame):
        if iter_count[0] >= iterations:
            anim.event_source.stop()
            return

        result = farm.run_iteration()
        iter_count[0] += 1
        
        ax1.clear()
        ax2.clear()
        
        ax1.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        
        if farm.sequential:
            ax1.set_title(f'Iteration {iter_count[0]}: Sequential Routes', fontsize=14)
            
            for route in result:
                if route:
                    ra = np.array(route)
                    ax1.plot(ra[:, 1], ra[:, 0], 'b-', alpha=0.3, linewidth=0.5)
            
            ax1.plot(farm.start[1], farm.start[0], 'go', markersize=15, label='Start')
            for idx, e in enumerate(farm.ends):
                ax1.plot(e[1], e[0], 'ro', markersize=12, label=f'Stop {idx+1}')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            pher_disp = np.copy(farm.pheromone)
            pher_disp[farm.obstacles] = 0
            
            ax2.imshow(pher_disp, cmap='YlOrRd', alpha=0.8)
            ax2.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
            ax2.set_title(f'Best Route: {farm.best_route_length:.0f} steps', fontsize=14)
            
            if farm.best_route:
                ba = np.array(farm.best_route)
                ax2.plot(ba[:, 1], ba[:, 0], 'lime', linewidth=3, label='Best Route')
                
                for idx in range(len(farm.ends)):
                    if idx < len(farm.ends):
                        e = farm.ends[idx]
                        ax2.plot(e[1], e[0], 'ro', markersize=12)
                        ax2.text(e[1]+1, e[0]+1, str(idx+1), color='white', 
                                fontsize=12, fontweight='bold')
            
            ax2.plot(farm.start[1], farm.start[0], 'go', markersize=15, label='Start')
            if farm.return_to_start:
                ax2.text(farm.start[1]+1, farm.start[0]+1, 'S/E', color='white',
                        fontsize=12, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
        else:
            ax1.set_title(f'Iteration {iter_count[0]}: Ant Paths', fontsize=14)
            
            for idx, (target, paths) in enumerate(result.items()):
                c = colors[idx % len(colors)]
                for path in paths:
                    if path:
                        pa = np.array(path)
                        ax1.plot(pa[:, 1], pa[:, 0], c=c, alpha=0.3, linewidth=0.5)
            
            ax1.plot(farm.start[1], farm.start[0], 'go', markersize=15, label='Start')
            for idx, e in enumerate(farm.ends):
                c = colors[idx % len(colors)]
                ax1.plot(e[1], e[0], 'o', color=c, markersize=12, label=f'End {idx+1}')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            pher_disp = np.copy(farm.pheromone)
            pher_disp[farm.obstacles] = 0
            
            ax2.imshow(pher_disp, cmap='YlOrRd', alpha=0.8)
            ax2.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
            
            total_len = sum([farm.best_path_lengths[e] for e in farm.ends if farm.best_path_lengths[e] != float('inf')])
            ax2.set_title(f'Total Best: {total_len:.0f} steps', fontsize=14)
            
            for idx, e in enumerate(farm.ends):
                if farm.best_paths[e]:
                    c = colors[idx % len(colors)]
                    ba = np.array(farm.best_paths[e])
                    ax2.plot(ba[:, 1], ba[:, 0], c=c, linewidth=3, 
                            label=f'Path {idx+1}: {farm.best_path_lengths[e]:.0f}')
            
            ax2.plot(farm.start[1], farm.start[0], 'go', markersize=15)
            for idx, e in enumerate(farm.ends):
                c = colors[idx % len(colors)]
                ax2.plot(e[1], e[0], 'o', color=c, markersize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    anim = animation.FuncAnimation(fig, update, frames=iterations, 
                                  interval=100, repeat=False)
    plt.show()
    
    return farm


if __name__ == "__main__":
    print("Ant Farm!!")
    print("\nRunning template layout. Change create_template_layout() to use your own.")
    print("Set sequential=True to visit endpoints in order.")
    print("Set return_to_start=True to return to starting point.\n")
    
    farm = create_template_layout()
    farm = visualize_ant_farm(farm, iterations=150)
    
    print("\nResults")
    if farm.sequential:
        print(f"Best sequential route: {farm.best_route_length:.0f} steps")
        if farm.best_route:
            print(f"Total waypoints: {len(farm.best_route)}")
    else:
        for idx, e in enumerate(farm.ends):
            plen = farm.best_path_lengths[e]
            print(f"Endpoint {idx+1} at {e}: {plen:.0f} steps")
            if farm.best_paths[e]:
                print(f"  Waypoints: {len(farm.best_paths[e])}")