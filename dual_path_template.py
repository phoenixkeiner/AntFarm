# Dual pathfinding with simple template layout for testing

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import random


# splits route into segments between waypoints
def split_route_into_segments(route, waypoints):
    if not route or not waypoints:
        return []

    segments = []
    route_list = list(route)
    current_segment = [route_list[0]]
    waypoint_idx = 0

    for i in range(1, len(route_list)):
        current_segment.append(route_list[i])

        if waypoint_idx < len(waypoints) and route_list[i] == waypoints[waypoint_idx]:
            segments.append(current_segment)
            current_segment = [route_list[i]]
            waypoint_idx += 1

    if len(current_segment) > 1:
        segments.append(current_segment)

    return segments


class DualPathFarm:
    # Ant farm with separate pathfinding for people and carts

    def __init__(self, grid_size=(50, 50), cart_size=None):
        self.grid_size = grid_size
        self.obstacles = np.zeros(grid_size, dtype=bool)
        self.start = None
        self.ends = []
        self.num_ants = 50
        self.evaporation_rate = 0.1
        self.pheromone_deposit = 100
        self.alpha = 1.0
        self.beta = 2.0
        self.sequential = True
        self.return_to_start = True

        # cart dimensions
        self.cart_size = cart_size if cart_size else (1, 1)

        # separate tracking for people and carts
        self.pheromone_people = np.ones(grid_size) * 0.1
        self.pheromone_carts = np.ones(grid_size) * 0.1
        self.best_route_people = None
        self.best_route_carts = None
        self.best_route_length_people = float('inf')
        self.best_route_length_carts = float('inf')
        self.all_routes_people = []
        self.all_routes_carts = []

    def set_start_end(self, start, end, sequential=False, return_to_start=False):
        self.start = start
        self.sequential = sequential
        self.return_to_start = return_to_start

        if isinstance(end, list):
            self.ends = end
        else:
            self.ends = [end]

    def add_obstacle(self, top_left, bottom_right):
        y1, x1 = top_left
        y2, x2 = bottom_right
        self.obstacles[y1:y2, x1:x2] = True

    def check_cart_collision(self, pos):
        y, x = pos
        cart_h, cart_w = self.cart_size

        if (y + cart_h > self.grid_size[0] or x + cart_w > self.grid_size[1]):
            return True

        cart_footprint = self.obstacles[y:y+cart_h, x:x+cart_w]
        return np.any(cart_footprint)

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

    def calculate_probability(self, current, nbrs, visited, target, pheromone_map):
        probs = []

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

                probs = self.calculate_probability(curr, nbrs, visited, target, pheromone_map)

                if sum(probs) == 0:
                    return None

                next_pos = random.choices(nbrs, weights=probs)[0]
                path.append(next_pos)
                visited.add(next_pos)
                curr = next_pos
            else:
                return None

        return full_route if full_route else None

    def run_iteration_dual(self):
        # Run pathfinding for both people and carts
        targets = self.ends.copy()
        if self.return_to_start:
            targets.append(self.start)

        # pathfinding for people (no cart constraints)
        routes_people = []
        for _ in range(self.num_ants):
            route = self.run_ant_sequential(self.start, targets,
                                          check_cart=False,
                                          pheromone_map=self.pheromone_people)
            routes_people.append(route)

        # pathfinding for carts (with cart constraints)
        routes_carts = []
        for _ in range(self.num_ants):
            route = self.run_ant_sequential(self.start, targets,
                                          check_cart=True,
                                          pheromone_map=self.pheromone_carts)
            routes_carts.append(route)

        # update pheromones for people
        self.pheromone_people *= (1 - self.evaporation_rate)
        self.pheromone_people = np.maximum(self.pheromone_people, 0.1)
        for route in routes_people:
            if route:
                self.all_routes_people.append(route)
                deposit = self.pheromone_deposit / len(route)
                for pos in route:
                    self.pheromone_people[pos] += deposit
                if len(route) < self.best_route_length_people:
                    self.best_route_length_people = len(route)
                    self.best_route_people = route

        # update pheromones for carts
        self.pheromone_carts *= (1 - self.evaporation_rate)
        self.pheromone_carts = np.maximum(self.pheromone_carts, 0.1)
        for route in routes_carts:
            if route:
                self.all_routes_carts.append(route)
                deposit = self.pheromone_deposit / len(route)
                for pos in route:
                    self.pheromone_carts[pos] += deposit
                if len(route) < self.best_route_length_carts:
                    self.best_route_length_carts = len(route)
                    self.best_route_carts = route

        return {'people': routes_people, 'carts': routes_carts}


def create_template_dual():
    # Create simple template layout for dual pathfinding
    farm = DualPathFarm(grid_size=(40, 60), cart_size=(2, 3))  # smaller cart for template

    farm.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)],
                       sequential=True, return_to_start=False)

    # add obstacles
    farm.add_obstacle((8, 10), (12, 30))
    farm.add_obstacle((20, 10), (24, 30))
    farm.add_obstacle((8, 35), (24, 45))
    farm.add_obstacle((28, 15), (32, 25))
    farm.add_obstacle((15, 48), (19, 58))

    return farm


def visualize_dual_paths(farm, iterations=100):
    # Visualize both people and cart paths side by side
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    iter_count = [0]
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']

    def update(frame):
        if iter_count[0] >= iterations:
            anim.event_source.stop()
            return

        result = farm.run_iteration_dual()
        iter_count[0] += 1

        # Panel 1: All routes overlay
        ax1.clear()
        ax1.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax1.set_title(f'Iteration {iter_count[0]}: All Routes', fontsize=12)

        for route in result['people']:
            if route:
                ra = np.array(route)
                ax1.plot(ra[:, 1], ra[:, 0], 'b-', alpha=0.15, linewidth=0.8)

        for route in result['carts']:
            if route:
                ra = np.array(route)
                ax1.plot(ra[:, 1], ra[:, 0], 'orange', alpha=0.15, linewidth=0.8)

        ax1.plot(farm.start[1], farm.start[0], 'go', markersize=12, label='Start')
        for idx, e in enumerate(farm.ends):
            ax1.plot(e[1], e[0], 'ro', markersize=10)
        ax1.plot([], [], 'b-', linewidth=2, label='People')
        ax1.plot([], [], 'orange', linewidth=2, label='Carts')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Panel 2: Best paths comparison
        ax2.clear()
        ax2.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        people_len = farm.best_route_length_people if farm.best_route_length_people != float('inf') else 0
        cart_len = farm.best_route_length_carts if farm.best_route_length_carts != float('inf') else 0
        diff = cart_len - people_len if people_len > 0 else 0
        ax2.set_title(f'Best Paths (Difference: {diff:.0f} steps)', fontsize=12)

        if farm.best_route_people:
            ba = np.array(farm.best_route_people)
            ax2.plot(ba[:, 1], ba[:, 0], 'b-', linewidth=4,
                    label=f'People: {farm.best_route_length_people:.0f} steps')

        if farm.best_route_carts:
            ba = np.array(farm.best_route_carts)
            ax2.plot(ba[:, 1], ba[:, 0], 'orange', linewidth=4,
                    label=f'Carts: {farm.best_route_length_carts:.0f} steps')

        ax2.plot(farm.start[1], farm.start[0], 'go', markersize=12)
        for idx, e in enumerate(farm.ends):
            ax2.plot(e[1], e[0], 'ro', markersize=10)
            ax2.text(e[1]+1, e[0]+1, str(idx+1), color='white',
                    fontsize=10, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Panel 3: People pheromone
        ax3.clear()
        pher_people = np.copy(farm.pheromone_people)
        pher_people[farm.obstacles] = 0
        ax3.imshow(pher_people, cmap='Blues', alpha=0.7)
        ax3.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax3.set_title('People Path', fontsize=12)
        if farm.best_route_people:
            waypoints = farm.ends.copy()
            if farm.return_to_start:
                waypoints.append(farm.start)
            segments = split_route_into_segments(farm.best_route_people, waypoints)

            for seg_idx, segment in enumerate(segments):
                if len(segment) > 1:
                    seg_array = np.array(segment)
                    color = colors[seg_idx % len(colors)]
                    ax3.plot(seg_array[:, 1], seg_array[:, 0], color=color,
                            linewidth=3, label=f'Seg {seg_idx+1}')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)

        # Panel 4: Cart pheromone
        ax4.clear()
        pher_carts = np.copy(farm.pheromone_carts)
        pher_carts[farm.obstacles] = 0
        ax4.imshow(pher_carts, cmap='YlOrRd', alpha=0.7)
        ax4.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax4.set_title('Cart Path', fontsize=12)
        if farm.best_route_carts:
            waypoints = farm.ends.copy()
            if farm.return_to_start:
                waypoints.append(farm.start)
            segments = split_route_into_segments(farm.best_route_carts, waypoints)

            for seg_idx, segment in enumerate(segments):
                if len(segment) > 1:
                    seg_array = np.array(segment)
                    color = colors[seg_idx % len(colors)]
                    ax4.plot(seg_array[:, 1], seg_array[:, 0], color=color,
                            linewidth=3, label=f'Seg {seg_idx+1}')

            # show cart size at start
            ba = np.array(farm.best_route_carts)
            cart_rect = Rectangle((ba[0][1], ba[0][0]), farm.cart_size[1], farm.cart_size[0],
                                fill=False, edgecolor='yellow', linewidth=2)
            ax4.add_patch(cart_rect)
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

    anim = animation.FuncAnimation(fig, update, frames=iterations,
                                  interval=100, repeat=False)
    plt.show()

    return farm


if __name__ == "__main__":
    print("Dual Pathfinding: People vs Carts (Template)")
    print("\nComparing optimal paths for:")
    print("  - People (small ants, no size constraints)")
    print("  - Carts (with size constraints)")
    print("\nBlue = People paths | Orange = Cart paths\n")

    farm = create_template_dual()
    farm = visualize_dual_paths(farm, iterations=150)

    print("\nResults")

    if farm.best_route_people:
        print(f"\nPeople best path: {farm.best_route_length_people:.0f} steps")
        print(f"  Routes tested: {len(farm.all_routes_people)}")

    if farm.best_route_carts:
        print(f"\nCart best path: {farm.best_route_length_carts:.0f} steps")
        print(f"  Routes tested: {len(farm.all_routes_carts)}")

    if farm.best_route_people and farm.best_route_carts:
        diff = farm.best_route_length_carts - farm.best_route_length_people
        pct = (diff / farm.best_route_length_people) * 100 if farm.best_route_length_people > 0 else 0
        print(f"\nDifference: Carts need {diff:.0f} extra steps ({pct:.1f}% longer)")

    print("\nComplete")
