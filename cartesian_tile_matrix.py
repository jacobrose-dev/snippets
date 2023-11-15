import pygame
import random
import math

"""generate_tile_matrix.py

Generates a Y-Flipped, Cartesian Coordinate Tiling System for use in a 2D top-down or isometric game.
Details how to translate a theoretical (X,Y) world coordinate (in meters) into a (Y,X) index for a grid data structure.

This ultimately allows for 2 powerful things to happen:
  1) sprites can use "real world" metrics for scaling and physics, i.e. they become decoupled from the screen and tiling system.
  2) a Camera() object can be "aimed" at a world coordinate, and only render the tiles or sprites within its view, i.e. "Occlusion Culling".

Things to note:
  The engine I'm using for this example is Pygame, which adhers to the SDL rendering order of top-left to bottom-right.
  The generated grid has an origin of (0,0), but no tile actually contains the origin. It's purely theoretical.
  The CLI representation of the 6 x 6 provided grid must be edited to show a larger or smaller grid in print_grid().
  You can change the grid size by editing SPAN, and change the theoretical tile size with METERS_PER_TILE.

It's important to understand why tile_bounds and grid_indexes are tightly coupled, while METERS_PER_TILE is not. Its strictly theoretical.
It can equal 0.1, 1, or 1000. It simply does not effective the tiling system, but it does effective the scale and distance of things.
Sprites, Camera(), and Graphics (for example, "blood stains on the ground") can operate on world coordinates (meters), independent of the tiling system (indexes).
This allows you to generate a much larger grid image than memory can allow without sacrificing performance by storing a full-size world image.
The world is now composed of tiles corresponding to world coordinates that are only rendered within view of a Camera().

You can now store thousands of extra sprites in the space freed up from having to store a full-size world image.

NOT PROVIDED HERE:
  To get the full effect of what I'm explaining here, you need a Tile() class containing self.blocks and a tile terrain image self.key.
  Each block in a tile is static, it doesn't move or change, and is represented by an image key, a center point, an angle to rotate the image, and a size in meters to scale the image.
  Blocks are essentially non-traversible areas of the world. If you're making a platformer, then you probably won't need block support, as everything is just tiles and sprites.
  Think: "a World() holding Tile()'s holding tuple blocks."
  
  Camera() is what facilitates the translation of world coordinates to screen pixels, but "focuses" a "lens" using world coordinates.
  It should be able to aim at a target, zoom smoothly in-and-out from that target and pan smoothly to-and-from targets.
  Think: "World() = (tiles, terrain, obstacles), Camera() = (metrics, rendering, tracking)"""

def pretty_print_xy_pair(xy):
    """Adds a + sign to positive numbers to make the grid more symmetrical."""
    x, y = xy
    if x > 0: x = f'+{x}'
    if y > 0: y = f'+{y}'
    print(f"({x},{y})", end=" ")
   
def print_grid(grid, span):
    print("\n\ngrid[span][span]", end=" = "); pretty_print_xy_pair(grid[span][span]); print()
    for row in grid:
        for tile in row:
            x, y = tile; pretty_print_xy_pair(tile)
            if x == -1: print("| ", end="")
        if grid.index(row) == span -1:
            print(); print("-" * 22, end =""); print("(0,0)", end =""); print("-" * 22)
    elif grid.index(row) != span*2 -1: print('\n                        |' * 2)

def print_rect(rect):
  print("\n",rect)
  pretty_print_xy_pair(rect.topleft); print("|", end=" "); pretty_print_xy_pair(rect.topright);
  print('\n          |'*2); print("-"* 8, end=""); pretty_print_xy_pair(rect.center); print("-"* 7, end="")
  print('\n          |'*2)
  pretty_print_xy_pair(rect.bottomleft); print("|", end=" "); pretty_print_xy_pair(rect.bottomright)
  print()

def get_containing_integer(float_number):
  """If float is positive, use ceil. If float is negative, use floor.
  If float is zero, return integer zero."""
  if float_number > 0: return math.ceil(float_number) # 0.5 = 1
  elif float_number < 0: return math.floor(float_number) # -0.5 = -1
  else: return 0 # float_number == 0.0, default to origin
  
def get_tile_bounds_containing_coordinate(world_rect, meters_per_tile, coordinate):
  """Returns the Cartesian Coordinate (tile, unit) containing the world coordinate.
  Returns None if coordinate falls outside of world boundaries."""
  x = get_containing_integer(coordinate[0] / meters_per_tile)
  y = get_containing_integer(coordinate[1] / meters_per_tile)
  if not world_rect.collidepoint(coordinate): return False, (x, y)
  return True, (x, y)

def account_for_nonexistence_of_zero(n, index):
  """Returns an index shifted by -1 if tile bound is greater than zero.
  This is needed because all 4 quadrants meet at (0,0), but none include it.
  It's strictly theorectical. No tile contains the plane's origin of (0, 0)."""
  if n > 0: return index - 1
  return index

def get_grid_index_containing_tile_bounds(grid_span, tile_bounds):
  """Returns grid index for (only) a valid tile_bounds, shifted using grid_span."""
  tx, ty = tile_bounds
  gy, gx = ( int(ty + (grid_span/2)), int(tx + (grid_span/2)) )
  gy, gx = ( account_for_nonexistence_of_zero(ty, gy), account_for_nonexistence_of_zero(tx, gx) )
  return (gy, gx)
  
def test_logic(tile_grid, meters_per_tile, world_rect, world_coordinate):
  """Prints the grid index of the tile that contains the coordinate provided.
  This is inferred, not searched, to increase performance with many tiles."""
  print("\n>>> world_xy", end=""); pretty_print_xy_pair(world_coordinate); print(f"@ {meters_per_tile} meters per tile")
  
  coord_is_within_world, tile_bounds = get_tile_bounds_containing_coordinate(world_rect, meters_per_tile, world_coordinate)
  print("\ntile_xy", end=""); pretty_print_xy_pair(tile_bounds)
  
  gy, gx = None, None
  if coord_is_within_world:
    gy, gx = get_grid_index_containing_tile_bounds(len(grid), tile_bounds)
    print(f"= index(y{gy},x{gx})")

  if gy or gx is not None:
    print(f"grid[y{gy}][x{gx}] = tile", end=""); pretty_print_xy_pair(grid[gy][gx]); print()

def switch_case_IO(tile_grid, meters_per_tile, world_rect):
  """Just the program's switch/case Input/Output handler. Prompts user for any world coordinate, or generates a valid one."""
  x, y = None, None
  match input("\nOptions: (Enter) random valid (0) exit (1) input x,y (2) show rect (3) show grid\nInput: "):
    case "0": return False
    case "":
      half_span_in_meters = span * meters_per_tile
      x = round(random.uniform(-half_span_in_meters, half_span_in_meters), 3) # millimeter precision
      y = round(random.uniform(-half_span_in_meters, half_span_in_meters), 3) # millimeter precision
    case "1":
      try:
        x = float(input("Cartesian Coordinate X: "))
        y = float(input("Cartesian Coordinate Y: "))
      except ValueError:
        print("Error: input could not be converted to a float()")
        return True
  test_logic(tile_grid, meters_per_tile, world_rect, (x, y))
  return True

"""Execution Threshold"""
span = 3 # tiles per quadrant minus origin for x axis and y axis
grid = []
for y in range(-span, span+1): # rows
  if y == 0: continue
  row = []
  for x in range(-span, span+1): # columns
    if x == 0: continue
    row.append((x,y))
  grid.append(row)
print_grid(grid, span)

meters_per_tile = 5.0   # can be any floating point number, but >= 1 works best for collisions
print("\n\nmeters per tile:", meters_per_tile)

half_span_in_meters = span * meters_per_tile
rect = pygame.Rect(-half_span_in_meters, -half_span_in_meters, half_span_in_meters*2, half_span_in_meters*2)
print_rect(rect)

running = True
while running:
  running = switch_case_IO(grid, meters_per_tile, rect)
  
