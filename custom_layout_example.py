"""
custom layout examples for ant colony optimization
"""

import numpy as np
import matplotlib.pyplot as plt
from ant_farm_optimizer import AntFarm, visualize_ant_farm


# creates layout from 2d array where 0 = free, 1 = obstacle, 2 = start, 3 = ends
def create_custom_array_layout():
    print("\n1: Array Layout")
    
    layout = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 4, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0],
    ])
    
    f = AntFarm(grid_size=layout.shape)
    f.load_custom_layout(layout)
    
    # for sequential routing, set after loading layout
    f.sequential = True
    f.return_to_start = False
    
    return f


# builds floor layout programmatically with obstacles added individually
def create_my_production_floor():
    print("\n2: Programmatic Layout")
    
    h = 50
    w = 70
    
    f = AntFarm(grid_size=(h, w))
    
    # parallel mode: find independent paths
    # f.set_start_end(start=(5, 5), end=[(45, 65), (25, 65), (45, 35)])
    
    # sequential mode: visit in order (1->2->3)
    f.set_start_end(start=(5, 5), end=[(45, 65), (25, 65), (45, 35)], 
                    sequential=True, return_to_start=False)
    
    f.add_obstacle((8, 10), (15, 25))
    f.add_obstacle((20, 10), (27, 20))
    f.add_obstacle((8, 35), (18, 50))
    f.add_obstacle((22, 35), (35, 45))
    f.add_obstacle((35, 15), (42, 30))
    f.add_obstacle((15, 55), (25, 68))
    
    f.add_obstacle((0, 0), (2, w))
    f.add_obstacle((h-2, 0), (h, w))
    f.add_obstacle((0, 0), (h, 2))
    f.add_obstacle((0, w-2), (h, w))
    
    return f


# loads layout from csv file with values 0 = free, 1 = obstacle, 2 = start, 3 = ends
def create_from_csv_file(fn='floor_layout.csv'):
    print(f"\n3: CSV Layout from {fn}")
    
    try:
        layout = np.loadtxt(fn, delimiter=',', dtype=int)
        
        f = AntFarm(grid_size=layout.shape)
        f.load_custom_layout(layout)
        
        print(f"Layout loaded: {layout.shape[0]} x {layout.shape[1]} grid")
        return f
        
    except FileNotFoundError:
        print(f"File {fn} not found. Creating example CSV")
        
        ex = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
        ])
        
        np.savetxt(fn, ex, delimiter=',', fmt='%d')
        print(f"Example CSV created: {fn}")
        print("Edit this file and run again!")
        
        f = AntFarm(grid_size=ex.shape)
        f.load_custom_layout(ex)
        return f


# builds layout interactively by clicking on grid positions
def create_interactive_layout():
    print("\n4: Interactive Builder")
    print("click to add obstacles")
    print("press 't' for start, 'e' for end, numbers '3-9' for additional ends")
    print("press 'c' to clear, close window when done")
    
    gs = (30, 40)
    layout = np.zeros(gs, dtype=int)
    
    fig, ax = plt.subplots(figsize=(12, 9))
    im = ax.imshow(layout, cmap='tab10', vmin=0, vmax=9)
    ax.set_title("click=obstacle | t=start | e=end1 | 3-9=end2-8 | c=clear")
    ax.grid(True, alpha=0.3)
    
    mode = [1]
    
    def onclick(event):
        if event.inaxes == ax and event.xdata and event.ydata:
            x = int(round(event.xdata))
            y = int(round(event.ydata))
            
            if 0 <= y < gs[0] and 0 <= x < gs[1]:
                if mode[0] == 2:
                    layout[layout == 2] = 0
                elif mode[0] >= 3:
                    layout[layout == mode[0]] = 0
                
                layout[y, x] = mode[0]
                im.set_data(layout)
                fig.canvas.draw()
    
    def onkey(event):
        if event.key == 't':
            mode[0] = 2
            ax.set_title("start mode")
        elif event.key == 'e':
            mode[0] = 3
            ax.set_title("end mode (end 1)")
        elif event.key in '3456789':
            mode[0] = int(event.key)
            ax.set_title(f"end mode (end {int(event.key)-2})")
        elif event.key == 'c':
            layout[:] = 0
            im.set_data(layout)
            ax.set_title("layout cleared")
        elif event.key in ['1', 'o']:
            mode[0] = 1
            ax.set_title("obstacle mode")
        fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', onkey)
    
    plt.show()
    
    f = AntFarm(grid_size=gs)
    f.load_custom_layout(layout)
    
    np.savetxt('my_custom_layout.csv', layout, delimiter=',', fmt='%d')
    print("layout saved to: my_custom_layout.csv")
    
    return f


if __name__ == "__main__":
    # Set number of iterations here
    ITERATIONS = 200

    print("custom layout examples")
    print("\nchoose a method:")
    print("1. array layout")
    print("2. programmatic layout (recommended)")
    print("3. csv file")
    print("4. interactive builder")
    print()

    choice = input("enter choice (1-4) or press enter for default [2]: ").strip()

    if choice == '1':
        f = create_custom_array_layout()
    elif choice == '3':
        f = create_from_csv_file()
    elif choice == '4':
        f = create_interactive_layout()
    else:
        f = create_my_production_floor()

    print("\nrunning optimization")
    if f.sequential:
        print("sequential mode: visiting endpoints in order")
        if f.return_to_start:
            print("will return to start after visiting all endpoints")
    else:
        print("parallel mode: finding independent paths to each endpoint")

    f = visualize_ant_farm(f, iterations=ITERATIONS)
    
    print("done!")
    
    if f.sequential:
        print(f"best sequential route: {f.best_route_length:.0f} steps")
        if f.best_route:
            print(f"total waypoints: {len(f.best_route)}")
    else:
        for idx, e in enumerate(f.ends):
            plen = f.best_path_lengths[e]
            print(f"endpoint {idx+1} at {e}: {plen:.0f} steps")
            if f.best_paths[e]:
                path = f.best_paths[e]
                print(f"waypoints (every 5th): {[path[i] for i in range(0, len(path), 5)]}")