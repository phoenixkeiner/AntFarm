# Ant Farm Production Floor Optimizer - Instructions

## Purpose

This ant colony optimization program finds the best paths through your production floor. The program can find separate paths to multiple destinations or create ordered routes that visit locations in sequence.

- More ants: Better for complex layouts with many obstacles
- Lower evaporation: Good for stable paths
- Higher beta: Prioritizes shorter paths
- More iterations: 100-200 for simple layouts, 300+ for complex layouts

## Setup

1. **Install required software:**
   ```bash
   pip install numpy matplotlib
   ```

2. **Run the example:**
   ```bash
   python ant_farm_optimizer.py
   ```
   
   This displays a working example with a sample production floor layout.

## Creating Your Own Layout

### 1: Modify the Template Function

Edit the `create_template_layout()` function in `ant_farm_optimizer.py`:

```python
def create_template_layout():
    f = AntFarm(grid_size=(40, 60))
    
    # parallel mode: find separate paths
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55)])
    
    # sequential mode: visit in order (endpoint 1, then 2, then 3)
    f.set_start_end(start=(5, 5), end=[(35, 55), (10, 55), (35, 25)],
                    sequential=True, return_to_start=False)
    
    f.add_obstacle((8, 10), (12, 30))
    f.add_obstacle((20, 10), (24, 30))
    
    return f
```

### 2: Import from Array

Create a layout from a 2D array where:
- `0` = open space
- `1` = obstacle (wall or machine)
- `2` = start point
- `3` = first endpoint
- `4` = second endpoint
- `5-9` = additional endpoints (maximum 7 total endpoints)

```python
import numpy as np

layout = np.array([
    [0, 0, 0, 2, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 0, 0, 3, 0, 4],
])

f = AntFarm(grid_size=layout.shape)
f.load_custom_layout(layout)

# set sequential mode after loading
f.sequential = True
f.return_to_start = False
```

### 3: Create from Floor Plan Image

See `custom_layout_example.py` for complete examples.

## Routing Modes

### Parallel Mode
Finds the best path from start to each endpoint independently. Each endpoint is treated as a separate destination.

This is for when you need paths to multiple locations but order does not matter.

### Sequential Mode
Creates a single route that visits all endpoints in the order provided. The program finds: Start -> Endpoint 1 -> Endpoint 2 -> Endpoint 3.

This is for when you must visit locations in a specific order, such as a delivery route or manufacturing process.

Enable with: `sequential=True` in `set_start_end()`

### Return to Start
When combined with sequential mode, the program creates a complete loop that returns to the starting point after visiting all endpoints.

Enable with: `return_to_start=True` in `set_start_end()`

Example: Start -> Stop 1 -> Stop 2 -> Stop 3 -> Back to Start

## Parameter Adjustment

Modify these values in the `AntFarm` class for improved results:

```python
self.num_ants = 20              # more ants search more paths
self.evaporation_rate = 0.1     # higher values erase old trails faster (0.05-0.3)
self.pheromone_deposit = 100    # trail strength
self.alpha = 1.0                # trail following strength (0.5-2.0)
self.beta = 2.0                 # distance preference (1.0-5.0)
```

## Measuring Your Floor

1. Select a scale:
   - Example: 1 grid unit = 2 feet
   - A 100 foot x 150 foot floor = 50 x 75 grid

2. Convert obstacles:
   - Measure position and size of each machine
   - Convert to grid positions
   - Note: y-position increases downward, x-position increases rightward

3. Example:
   ```
   Actual: Machine at (20 feet, 30 feet) with size 10 feet x 15 feet
   Scale: 1 unit = 2 feet
   Grid: Position (10, 15) with size 5 x 7.5 -> round to (10, 15) to (15, 23)
   
   f.add_obstacle((10, 15), (15, 23))
   ```

## Understanding the Display

The program shows two panels:

**Left Panel - Ant Paths:**
- Colored lines: Current ant searches. different colors for different endpoints
- Green dot: Start point
- Colored dots: Endpoint colors match path colors
- Gray areas: Obstacles

In sequential mode, all ants follow the same color because they all visit endpoints in the same order.

**Right Panel - Pheromone Map:**
- Red/Yellow colors: Pheromone strength (red = higher)
- Colored lines: Best paths found to each endpoint (parallel mode)
- Green line: Best complete route (sequential mode)
- Numbers show visit order in sequential mode

**Path Length:**
- Displayed in title and legend
- Smaller number = better path
- Length measured in grid units

## Applications

1. **Layout Planning:**
   - Test equipment arrangements
   - Find best paths before installation

2. **Traffic Analysis:**
   - Identify congestion points
   - Plan traffic flow

3. **Emergency Planning:**
   - Find quickest exit routes
   - Multiple exit support

4. **Material Handling:**
   - Optimize routes to multiple locations
   - Minimize transport time
   - Plan delivery sequences

## Limitations

- Two-dimensional only
- Assumes constant movement speed
- Does not model traffic congestion
- Grid-based. diagonal movements are approximate

## If youre runnning into issues

**Ants not finding path:**
- Verify start and endpoints are not inside obstacles
- Confirm valid path exists
- Increase iterations or ant count
- Decrease beta parameter

**Path appears incorrect:**
- Run more iterations (200-500)
- Increase num_ants
- Adjust alpha and beta values

**Display too slow:**
- Reduce grid size
- Reduce num_ants
- Increase animation interval in visualize_ant_farm()

## Procedure

1. Run template layout first
2. Measure your production floor
3. Create simple version with main obstacles
4. Test and adjust parameters
5. Add more detail as needed