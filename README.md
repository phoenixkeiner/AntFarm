# Ant Colony Optimizer for Production Floor Layout

This program finds the best routes through the production floor using ant colony optimization. This can find paths to multiple destinations or create ordered routes that visit locations in sequence.

## Whats included in my repo

- **ant_farm_optimizer.py** - Main program with example layout
- **custom_layout_example.py** - Four methods to build your own layout
- **INSTRUCTIONS.md** - Complete setup and usage guide
- **floor_layout_template.csv** - Spreadsheet template for layouts

## Installation

```bash
pip install numpy matplotlib
python ant_farm_optimizer.py
```

The program displays two animated panels:
- Left panel: Ants searching for paths in real time
- Right panel: Heat map showing the best paths found

## Creating Your Layout

### 1: Edit the template

Open `ant_farm_optimizer.py` and modify the `create_template_layout()` function:

```python
def create_template_layout():
    f = AntFarm(grid_size=(40, 60))
    
    # parallel mode: find separate paths to each endpoint
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55)])
    
    # sequential mode: visit endpoints in order. 1 then 2 then 3 and so on.
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)],
                    sequential=True, return_to_start=False)
    
    # add obstacles
    f.add_obstacle((8, 10), (12, 30))
    return f
```

### 2: Use spreadsheet file

Edit `floor_layout_template.csv` in Excel:
- 0 = open space
- 1 = obstacle
- 2 = start point
- 3 = first endpoint
- 4 = second endpoint
- 5-9 = additional endpoints

Run: `python custom_layout_example.py` and select option 3

### 3: Interactive builder

Run `python custom_layout_example.py` and select option 4. Click to place obstacles, press 's' for start, 'e' for first endpoint, '4'-'9' for more endpoints.

## Routing Modes

### Parallel Mode
Finds the best path from start to each endpoint independently. Use this when you have multiple destinations and order does not matter.

### Sequential Mode
Visits endpoints in the order provided. The program finds the best route that goes: Start -> Endpoint 1 -> Endpoint 2 -> Endpoint 3 (and so on).

Set `sequential=True` to enable this mode. Set `return_to_start=True` to return to the starting point after visiting all endpoints.

Example: Delivery truck visiting stops 1, 2, 3, then returning to depot.

## Parameter Adjustment

Open `ant_farm_optimizer.py` and modify these values:

```python
self.num_ants = 20              # more ants search more options
self.evaporation_rate = 0.1     # higher values forget old paths faster
self.alpha = 1.0                # how much ants follow pheromone trails
self.beta = 2.0                 # how much ants prefer shorter distances
```

Run more iterations (like 150 to 500) for complex layouts. Change the number in `visualize_ant_farm(farm, iterations=150)`.

## Measurement Conversion

Select a scale, such as 1 grid unit = 2 feet. Convert all measurements:

```
Actual floor: 100 feet x 150 feet  ->  Grid: 50 x 75
Machine at (20 feet, 30 feet), size 10 feet x 15 feet  ->  Grid: (10, 15) to (15, 23)
```

## Applications

- Testing equipment arrangements before installation
- Finding traffic bottlenecks
- Planning delivery routes with multiple stops
- Designing evacuation routes with multiple exits
- General pathfinding with obstacles

## How it works

The program simulates ant behavior in nature. Ants leave chemical trails (pheromones) as they search for food. Shorter paths accumulate more pheromone because ants complete them faster. Other ants follow stronger pheromone trails, reinforcing good paths. Poor paths fade over time. The colony discovers the optimal route through this process.

This is used in shipping logistics, vehicle routing, network design and similar problems.

## Problem Solving

**No path found?**
- Verify start and endpoints are not inside obstacles
- Confirm a valid path exists
- Increase iterations or ant count

**Path appears incorrect?**
- Run more iterations (200-500)
- Increase `num_ants` to 30-50
- Reduce `beta` value

See INSTRUCTIONS.md for additional information.