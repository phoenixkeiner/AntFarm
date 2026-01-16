# Cart simulation for 3ft x 5ft warehouse carts

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ant_farm_optimizer import AntFarm, visualize_ant_farm, split_route_into_segments


def create_warehouse_with_carts(scale=2):
    h = 120
    w = 180
    cart_h = 3 * scale
    cart_w = 5 * scale

    print(f"\nWarehouse Layout:")
    print(f"  Grid size: {h} x {w} (each unit = {12/scale} inches)")
    print(f"  Cart size: {cart_h} x {cart_w} units (3ft x 5ft)")
    print(f"  Actual warehouse: {h/(2*scale)}ft x {w/(2*scale)}ft")

    farm = AntFarm(grid_size=(h, w), cart_size=(cart_h, cart_w))
    farm.num_ants = 50 # higher the number the more accurate the tests will be.
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


def visualize_cart_paths(farm, iterations=150):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    iter_count = [0]
    colorbar_ref = [None]
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']

    def update(frame):
        if iter_count[0] >= iterations:
            anim.event_source.stop()
            return

        result = farm.run_iteration()
        iter_count[0] += 1

        ax1.clear()
        ax1.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax1.set_title(f'Iteration {iter_count[0]}: Cart Routes', fontsize=12)
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

        ax2.clear()
        pher_disp = np.copy(farm.pheromone)
        pher_disp[farm.obstacles] = 0
        ax2.imshow(pher_disp, cmap='YlOrRd', alpha=0.7)
        ax2.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax2.set_title(f'Best Route: {farm.best_route_length:.0f} steps', fontsize=12)
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
        ax2.plot(farm.start[1], farm.start[0], 'go', markersize=12)
        for idx, e in enumerate(farm.ends):
            ax2.plot(e[1], e[0], 'ro', markersize=10)
            ax2.text(e[1]+2, e[0]+2, str(idx+1), color='white', fontsize=10, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.2)

        ax3.clear()
        traffic_display = np.copy(farm.traffic_heatmap).astype(float)
        traffic_display[farm.obstacles] = np.nan
        im = ax3.imshow(traffic_display, cmap='hot', interpolation='nearest')
        ax3.imshow(farm.obstacles, cmap='Greys', alpha=0.3)
        ax3.set_title(f'Traffic Heatmap (Total Routes: {len(farm.all_routes)})', fontsize=12)
        if iter_count[0] % 10 == 0:
            bottlenecks = farm.detect_bottlenecks()
            if bottlenecks:
                for bn in bottlenecks[:10]:
                    y, x = bn['position']
                    ax3.plot(x, y, 'c*', markersize=15, markeredgecolor='blue', markeredgewidth=1)
                    ax3.text(x+2, y, f"{bn['traffic_count']}", color='cyan', fontsize=8, fontweight='bold')
        if colorbar_ref[0] is None:
            colorbar_ref[0] = plt.colorbar(im, ax=ax3, label='Cart Passes')
        else:
            colorbar_ref[0].update_normal(im)
        ax3.grid(True, alpha=0.2)

        ax4.clear()
        ax4.axis('off')

        stats_text = f"Cart Simulation\n\n"
        stats_text += f"Iteration: {iter_count[0]}/{iterations}\n\n"
        stats_text += f"Cart: 3ft x 5ft ({farm.cart_size[0]}x{farm.cart_size[1]} units)\n"
        stats_text += f"Routes: {len(farm.all_routes)}\n\n"

        if farm.best_route:
            stats_text += f"Best: {farm.best_route_length:.0f} steps (~{farm.best_route_length * 0.5:.1f}ft)\n\n"

        if iter_count[0] % 10 == 0 and iter_count[0] > 0:
            bottlenecks = farm.detect_bottlenecks()
            if bottlenecks:
                stats_text += f"Bottlenecks: {len(bottlenecks)}\n"
                for bn in bottlenecks[:3]:
                    stats_text += f"  {bn['traffic_count']} passes, {bn['clearance']} clear\n"
                stats_text += "\n"

            conflicts = farm.analyze_route_conflicts(time_window=20)
            if conflicts:
                stats_text += f"Conflicts: {len(conflicts)}\n\n"

        if iter_count[0] > 50:
            max_traffic = np.max(farm.traffic_heatmap[~farm.obstacles])
            avg_traffic = np.mean(farm.traffic_heatmap[farm.traffic_heatmap > 0])
            stats_text += f"Peak: {int(max_traffic)} | Avg: {avg_traffic:.1f}\n\n"
            if max_traffic > avg_traffic * 3:
                stats_text += "High congestion detected\n"
                stats_text += "Widen aisles / Alt routes / Stagger times\n"

        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()

    anim = plt.matplotlib.animation.FuncAnimation(fig, update, frames=iterations,
                                                  interval=100, repeat=False)
    plt.show()

    return farm


def print_detailed_analysis(farm):
    print("Final Analysis")

    print(f"\nCart: 3ft x 5ft ({farm.cart_size[0]}x{farm.cart_size[1]} units)")
    print(f"Routes: {len(farm.all_routes)}")

    if farm.best_route:
        print(f"\nBest: {farm.best_route_length:.0f} steps (~{farm.best_route_length * 0.5:.1f}ft)")

    bottlenecks = farm.detect_bottlenecks()
    print(f"\nBottlenecks: {len(bottlenecks)}")
    if bottlenecks:
        for bn in sorted(bottlenecks, key=lambda x: x['traffic_count'], reverse=True)[:5]:
            print(f"  {bn['position']}: {bn['traffic_count']} passes, {bn['clearance']} clear")

    conflicts = farm.analyze_route_conflicts(time_window=30)
    print(f"\nConflicts: {len(conflicts)}")
    if conflicts:
        conflict_positions = {}
        for c in conflicts:
            pos = c['position']
            conflict_positions[pos] = conflict_positions.get(pos, 0) + 1
        sorted_conflicts = sorted(conflict_positions.items(), key=lambda x: x[1], reverse=True)
        for pos, count in sorted_conflicts[:5]:
            print(f"  {pos}: {count}")

    non_zero_traffic = farm.traffic_heatmap[farm.traffic_heatmap > 0]
    if len(non_zero_traffic) > 0:
        peak = int(np.max(non_zero_traffic))
        avg = np.mean(non_zero_traffic)
        print(f"\nTraffic - Peak: {peak} | Avg: {avg:.1f}")

        if peak > avg * 3:
            print("  High congestion - widen aisles, alt routes, stagger times")
        if len(bottlenecks) > 5:
            print("  Multiple bottlenecks - review aisle widths")
        if len(conflicts) > 20:
            print("  High collision risk - add traffic control")


if __name__ == "__main__":
    # Set number of iterations here
    ITERATIONS = 150

    print("Warehouse Cart Pathfinding Simulation")
    print("3ft x 5ft Carts\n")

    farm = create_warehouse_with_carts(scale=2)

    print("Finding optimal routes, detecting bottlenecks, analyzing conflicts\n")

    farm = visualize_cart_paths(farm, iterations=ITERATIONS)

    print_detailed_analysis(farm)

    print("\nComplete")
