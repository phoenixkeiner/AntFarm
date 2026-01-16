# Ant Colony Optimizer for Production Floor Layout

This program finds the best routes through the production floor using ant colony optimization. This can find paths to multiple destinations or create ordered routes that visit locations in sequence.

## Files in This Repository

### Core Files

**ant_farm.py** - Main ant colony optimization engine
- Contains the AntFarm class with all pathfinding logic
- Implements ant colony optimization algorithm with pheromone tracking
- Supports both parallel mode, independent paths to each endpoint and sequential mode for an ordered route through all endpoints.
- Includes cart size collision detection for larger objects
- Has template layout function that can be modified
- Run this file directly to see the example template in action

**custom_layout.py** - Four methods to build your own layout
- Method 1: Array layout using numpy arrays
- Method 2: Direct code layout using add_obstacle function
- Method 3: CSV file import from spreadsheet
- Method 4: Interactive layout builder (click to place obstacles and endpoints)
- Run this file and choose which method to use

**cart_visualization.py** - Route finding visualization for carts
- Shows 2 panels: current routes being tested and best route found
- Displays cart footprint at key positions along the route
- Color-coded route segments for sequential pathfinding
- Designed for real warehouse cart pathfinding with 3ft x 5ft carts
- Run this for quick route visualization

**ants_and_carts.py** - Simultaneous pathfinding for people and carts
- Runs two separate pathfinding algorithms at the same time
- People paths (blue): no size constraints, can use narrow spaces
- Cart paths (orange): must account for 3ft x 5ft cart size
- Shows 4 panels: all routes overlay, best paths comparison, people route, cart route
- Calculates and displays the extra distance carts need compared to people
- Uses separate pheromone maps so people and carts don't interfere with each other
- Full warehouse layout with realistic dimensions

**ants_and_carts_templates.py** - Dual pathfinding with simple template layout
- Same dual pathfinding as ants_and_carts.py but with smaller test layout
- Faster to run for quick testing
- Good for understanding how dual pathfinding works before running full warehouse simulation

### Support Files

**floor_layout_template.csv** - Spreadsheet template for layouts
- Use with custom_layout.py method 3
- Edit in Excel or any spreadsheet program
- 0 = open space, 1 = obstacle, 2 = start point, 3-9 = endpoints

## Installation for New Computers

### Windows Installation

1. Download and install Python
   - Go to https://www.python.org/downloads/
   - Download Python 3.10 or newer
   - Run installer and check the box that says "Add Python to PATH"
   - Click "Install Now"

2. Install required packages
   - In Command Prompt, type:
   ```
   pip install numpy matplotlib
   ```

3. Download this repository
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract the ZIP file to your Documents folder

4. Run the program
   - In Command Prompt, navigate to the folder:
   ```
   cd Documents\AntFarm
   ```
   - Run any of the Python files:
   ```
   python ant_farm.py
   python cart_visualization.py
   python ants_and_carts.py
   ```

### Mac Installation

1. Install Python
   - Go to https://www.python.org/downloads/
   - Download Python 3.10 or newer for macOS
   - Run the installer and follow prompts

2. Install required packages
   - In Terminal, type:
   ```
   pip3 install numpy matplotlib
   ```

3. Download this repository
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract to your Documents folder

4. Run the program
   - In Terminal, navigate to the folder:
   ```
   cd Documents/AntFarm
   ```
   - Run any of the Python files:
   ```
   python3 ant_farm.py
   python3 cart_visualization.py
   python3 ants_and_carts.py
   ```

## Quick Start

After installation, try these in order:

1. Basic pathfinding with template layout:
   ```
   python ant_farm.py
   ```

2. Warehouse cart route visualization:
   ```
   python cart_visualization.py
   ```

3. Compare people vs cart paths (template):
   ```
   python ants_and_carts_templates.py
   ```

4. Full dual pathfinding simulation:
   ```
   python ants_and_carts.py
   ```

5. Build your own layout:
   ```
   python custom_layout.py
   ```

## What the Program Shows

The program displays animated visualizations showing:
- Left panel: Ants searching for paths in real time
- Right panel: Best routes found
- For dual pathfinding: Side-by-side comparison of people paths (blue) and cart paths (orange)

## Creating Your Layout

### Method 1: Edit the template in code

Open ant_farm.py and modify the create_template_layout function:

```python
def create_template_layout():
    f = AntFarm(grid_size=(40, 60))

    # parallel mode: find separate paths to each endpoint
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55)])

    # sequential mode: visit endpoints in order
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)],
                    sequential=True, return_to_start=False)

    # add obstacles (top_left corner, bottom_right corner)
    f.add_obstacle((8, 10), (12, 30))
    return f
```

### Method 2: Use spreadsheet file

Edit floor_layout_template.csv in Excel:
- 0 = open space
- 1 = obstacle
- 2 = start point
- 3 = first endpoint
- 4 = second endpoint
- 5-9 = additional endpoints

Run: python custom_layout.py and select option 3

### Method 3: Interactive builder

Run python custom_layout.py and select option 4
- Click to place obstacles
- Press 't' for start point
- Press 'e' for first endpoint
- Press '4' through '9' for additional endpoints
- Press 'q' to finish and run optimization

## Routing Modes

### Parallel Mode
Finds the best path from start to each endpoint independently. Use this when you have multiple destinations and order does not matter.

```python
f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55)])
```

### Sequential Mode
Visits endpoints in the order provided. The program finds the best route that goes: Start to Endpoint 1 to Endpoint 2 to Endpoint 3 and so on.

```python
f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)],
                sequential=True, return_to_start=False)
```

Set return_to_start=True to return to the starting point after visiting all endpoints.

Example: Delivery truck visiting stops 1, 2, 3, then returning to depot.

## Speed vs Accuracy Adjustment

All simulation files have two key parameters you can adjust for faster/slower and less/more accurate results:

### 1. Number of Ants (num_ants)
Controls how many paths are tested each iteration:
- **Fast mode (10-20 ants)**: Quick results, good for testing layouts
- **Balanced mode (30-50 ants)**: Good balance of speed and accuracy
- **Accurate mode (50-100 ants)**: Slower, finds better paths

Example in code:
```python
farm.num_ants = 20  # Change this value
```

### 2. Number of Iterations (ITERATIONS)
Controls how many rounds of optimization to run:
- **Fast mode (10-50 iterations)**: Quick preview, may not find optimal path
- **Balanced mode (50-100 iterations)**: Usually sufficient for most layouts
- **Thorough mode (100-200 iterations)**: Best results for complex layouts

Example at bottom of each file:
```python
ITERATIONS = 10  # Change this value
```

### Speed Comparison
- **ant_farm.py**: Default 10 iterations, 50 ants = FAST
- **cart_visualization.py**: Default 10 iterations, 20 ants = FAST
- **ants_and_carts.py**: Default 150 iterations, 50 ants = SLOW
- **ants_and_carts_templates.py**: Default 150 iterations, 50 ants = SLOW

**Tip**: Start with fast settings (10 iterations, 20 ants) to test your layout. Once you're happy with it, increase to 100 iterations and 50 ants for final optimization.

## Parameter Adjustment

Open ant_farm.py and modify these values in the AntFarm class:

```python
self.num_ants = 50              # more ants search more options (higher accuracy)
self.evaporation_rate = 0.1     # higher values forget old paths faster
self.alpha = 1.0                # how much ants follow pheromone trails
self.beta = 2.0                 # how much ants prefer shorter distances
```

## Measurement Conversion

Select a scale, such as 1 grid unit = 2 feet. Convert all measurements:

```
Actual floor: 100 feet x 150 feet  ->  Grid: 50 x 75
Machine at (20 feet, 30 feet), size 10 feet x 15 feet  ->  Grid: (10, 15) to (15, 23)
```

For cart_visualization.py, the scale parameter controls this:
- scale=2 means 1 grid unit = 6 inches (0.5 feet)
- scale=1 means 1 grid unit = 12 inches (1 foot)

## Understanding Dual Pathfinding

The dual pathfinding files (ants_and_carts.py and ants_and_carts_templates.py) show the difference between optimal paths for:
- People: small, can navigate narrow spaces, shown in blue
- Carts: 3ft x 5ft, need wider clearances, shown in orange

This is useful for:
- Determining if aisles are wide enough for carts
- Finding how much extra distance carts need to travel
- Identifying where separate people-only shortcuts can be added
- Optimizing floor layout for both pedestrian and cart traffic

## Applications

- Testing equipment arrangements before installation
- Finding traffic bottlenecks in warehouses
- Planning delivery routes with multiple stops
- Designing evacuation routes with multiple exits
- Comparing pedestrian vs cart routing efficiency
- General pathfinding with obstacles

## How It Works

The program simulates ant behavior in nature. Ants leave pheromones as they search for food. Shorter paths accumulate more pheromone because ants complete them faster. Other ants follow stronger pheromone trails, reinforcing good paths. Poor paths fade over time. The colony discovers the optimal route through this process.

For more information about ants, please read this [Wikipedia article](https://en.wikipedia.org/wiki/Ant).

![Ant](https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Red_Ant_-_March_2025.jpg/250px-Red_Ant_-_March_2025.jpg)

This algorithm is used in shipping logistics, vehicle routing, network design and similar optimization problems.