# Cart route visualization for 3ft x 5ft warehouse carts

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ant_farm import AntFarm, visualize_ant_farm, split_route_into_segments


def create_warehouse_with_carts(scale=2):
    h = 120
    w = 180
    cart_h = 3 * scale
    cart_w = 5 * scale

    print(f"\nWarehouse layout:")
    print(f"Grid size: {h} x {w} (each unit = {12/scale} inches)")
    print(f"Cart size: {cart_h} x {cart_w} units (3ft x 5ft)")
    print(f"Actual warehouse: {h/(2*scale)}ft x {w/(2*scale)}ft")

    farm = AntFarm(grid_size=(h, w), cart_size=(cart_h, cart_w))
    # Adjust num_ants for accuracy vs speed tradeoff
    # Lower values (10-20) = faster but less accurate
    # Higher values (50-100) = slower but more accurate
    farm.num_ants = 20
    farm.segment_by_segment = True # optimize each leg independently

    start_pos = (10, 10)
    endpoints = [(100, 160), (50, 160), (100, 80)]
    farm.set_start_end(start=start_pos, end=endpoints, sequential=True, return_to_start=True)

    farm.add_obstacle((15, 30), (105, 45))
    farm.add_obstacle((15, 55), (105, 70))
    farm.add_obstacle((15, 95), (105, 110))
    farm.add_obstacle((15, 120), (105, 135))
    farm.add_obstacle((30, 145), (45, 175))
    farm.add_obstacle((70, 145), (85, 175))
    farm.add_obstacle((50, 0), (70, 20))
    farm.add_obstacle((0, 0), (2, w))
    farm.add_obstacle((h-2, 0), (h, w))
    farm.add_obstacle((0, 0), (h, 2))
    farm.add_obstacle((0, w-2), (h, w))

    return farm


def visualize_cart_routes(farm, iterations=150):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    iter_count = [0]
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']

    def update(frame):
        if iter_count[0] >= iterations:
            anim.event_source.stop()
            return

        result = farm.run_iteration()
        iter_count[0] += 1

        # Left panel: Current routes being tested
        ax1.clear()
        ax1.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax1.set_title(f'Iteration {iter_count[0]}: Cart Routes Being Tested', fontsize=12)
        for route in result:
            if route:
                ra = np.array(route)
                ax1.plot(ra[:, 1], ra[:, 0], 'b-', alpha=0.3, linewidth=1)
        ax1.plot(farm.start[1], farm.start[0], 'go', markersize=12, label='Start')
        for idx, e in enumerate(farm.ends):
            ax1.plot(e[1], e[0], 'ro', markersize=10, label=f'Stop {idx+1}')
        cart_rect = Rectangle((farm.start[1], farm.start[0]), farm.cart_size[1], farm.cart_size[0],
                              fill=False, edgecolor='green', linewidth=2)
        ax1.add_patch(cart_rect)
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.2)

        # Right panel: Best route found
        ax2.clear()
        ax2.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax2.set_title(f'Best Route Found: {farm.best_route_length:.0f} steps (~{farm.best_route_length * 0.5:.1f}ft)', fontsize=12)

        if farm.best_route:
            # split route into colored segments
            waypoints = farm.ends.copy()
            if farm.return_to_start:
                waypoints.append(farm.start)
            segments = split_route_into_segments(farm.best_route, waypoints)

            for seg_idx, segment in enumerate(segments):
                if len(segment) > 1:
                    seg_array = np.array(segment)
                    color = colors[seg_idx % len(colors)]
                    ax2.plot(seg_array[:, 1], seg_array[:, 0], color=color,
                            linewidth=3, label=f'Segment {seg_idx+1}')

            # show cart footprint at key positions
            ba = np.array(farm.best_route)
            for i in [0, len(ba)//3, 2*len(ba)//3, -1]:
                if i < len(ba):
                    pos = ba[i]
                    cart_rect = Rectangle((pos[1], pos[0]), farm.cart_size[1], farm.cart_size[0],
                                         fill=False, edgecolor='yellow', linewidth=1, alpha=0.5)
                    ax2.add_patch(cart_rect)

        ax2.plot(farm.start[1], farm.start[0], 'go', markersize=12, label='Start')
        for idx, e in enumerate(farm.ends):
            ax2.plot(e[1], e[0], 'ro', markersize=10, label=f'Stop {idx+1}' if idx == 0 else '')
            ax2.text(e[1]+2, e[0]+2, str(idx+1), color='white', fontsize=10, fontweight='bold')
        if farm.return_to_start:
            ax2.text(farm.start[1]+2, farm.start[0]+2, 'S/E', color='white', fontsize=10, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.2)

        plt.tight_layout()

    anim = plt.matplotlib.animation.FuncAnimation(fig, update, frames=iterations, interval=100, repeat=False)
    plt.show()

    return farm


def print_route_summary(farm):
    print("\nRoute summary")
    print(f"Cart: 3ft x 5ft ({farm.cart_size[0]}x{farm.cart_size[1]} units)")
    print(f"Routes tested: {len(farm.all_routes)}")

    if farm.best_route:
        print(f"Best route: {farm.best_route_length:.0f} steps (~{farm.best_route_length * 0.5:.1f}ft)")

        # Calculate segment distances
        waypoints = farm.ends.copy()
        if farm.return_to_start:
            waypoints.append(farm.start)
        segments = split_route_into_segments(farm.best_route, waypoints)

        print(f"\nRoute breakdown ({len(segments)} segments):")
        for seg_idx, segment in enumerate(segments):
            if len(segment) > 1:
                print(f"Segment {seg_idx+1}: {len(segment)} steps (~{len(segment) * 0.5:.1f}ft)")


if __name__ == "__main__":
    # Set number of iterations here
    # Lower values (10-50) = faster but less optimized
    # Higher values (100-200) = slower but more optimized
    ITERATIONS = 10

    print("Warehouse cart route visualization")
    print("3ft x 5ft carts\n")

    farm = create_warehouse_with_carts(scale=2)

    print("Finding optimal routes\n")

    farm = visualize_cart_routes(farm, iterations=ITERATIONS)

    print_route_summary(farm)

    print("\nComplete")
