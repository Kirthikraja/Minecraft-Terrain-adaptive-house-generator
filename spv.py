#!/usr/bin/env python3
import logging
import random
from termcolor import colored
from gdpc import Block, Editor
from gdpc import geometry as geo
# === Logging system ===
logging.basicConfig(format=colored("%(name)s - %(levelname)s - %(message)s", "yellow"))
# === GDPC Editor Initialization ===
ED = Editor(buffering=True)
BUILD_AREA = ED.getBuildArea()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last
WORLDSLICE = ED.loadWorldSlice(BUILD_AREA.toRect(), cache=True)
# === Configuration ===
AVGHEIGHT = 0  # Determined by terrain analysis
"--------------------------------------------------------------------------------------------"
FLOOR_BLOCK = Block("polished_andesite")
WALL_BLOCK = random.choice([ Block("white_terracotta"),Block("orange_terracotta"),Block("red_terracotta"), Block("sandstone"),Block("smooth_sandstone"),Block("stone_bricks")])
ROOF_BLOCK = Block("brick_stairs")
WINDOW_BLOCK = Block("glass_pane")
DOOR_BLOCK = Block("oak_door")
BOOKSHELF_BLOCK = random.choice([Block("bookshelf"),Block("lectern")])
GARDEN_BLOCK = Block("grass_block")
PATHWAY_BLOCK = Block("polished_andesite")
DECORATION_BLOCK = random.choice([Block("rose_bush"), Block("peony"), Block("oak_sapling"),Block("dandelion"), Block("poppy"), Block("blue_orchid"), Block("allium")])
light = {0: Block("lantern"), 1: Block("soul_lantern")}
light_type = random.choice(light)
LIGHT_BLOCK = light_type  # Lanterns for lighting
"----------------------------------------------------------------------------------------------"
def scanTerrain():
    """
    Analyze the terrain within BUILD_AREA and calculate the average height along the x-axis and z-axis center lines.
    """
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    # Calculate the midpoint along the x and z axes
    xaxis = STARTX + (LASTX - STARTX) // 2  # Midpoint of x-axis
    zaxis = STARTZ + (LASTZ - STARTZ) // 2  # Midpoint of z-axis
    print("Calculating stable terrain height...")
    # Calculate the height along the x-axis center line
    y = heights[(xaxis - STARTX, zaxis - STARTZ)]  # Start with the middle point height
    for x in range(STARTX, LASTX + 1):
        newy = heights[(x - STARTX, zaxis - STARTZ)]  # Height along the z-axis center line
        y = (y + newy) // 2  # Progressive averaging
    # Calculate the height along the z-axis center line
    for z in range(STARTZ, LASTZ + 1):
        newy = heights[(xaxis - STARTX, z - STARTZ)]  # Height along the x-axis center line
        y = (y + newy) // 2  # Progressive averaging
    global AVGHEIGHT
    AVGHEIGHT = y
    logging.info(f"Calculated stable terrain height: {AVGHEIGHT}")

def buildHouse(x, z):
    y = AVGHEIGHT
    # === Build the house ===
    geo.placeCuboidHollow(ED, (x, y, z), (x + 15, y + 6, z + 20), WALL_BLOCK)
    # === Front door (north-facing wall) ===
    door_y = y + 1  # Height of the door base
    front_door_z = z + 10  # Midpoint of the north-facing wall
    ED.placeBlock((x, door_y, front_door_z), DOOR_BLOCK)
    # Ensure no additional openings near the front door
    for dz in range(z + 1, z + 20):
        if dz != front_door_z:
            for dy in range(y + 1, y + 4):
                ED.placeBlock((x, dy, dz), WALL_BLOCK)
     # === Back door (south-facing wall) ===
    back_door_z = z + 10
    ED.placeBlock((x + 15, door_y, back_door_z), DOOR_BLOCK)
    logging.info("North (front) and south (back) doors placed.")
    # === Build the compound wall ===
    WALL_OFFSET = 25  # Increased distance from the house to the compound wall
    house_length = 20
    house_width = 15
    wall_start_x = x - WALL_OFFSET
    wall_start_z = z - WALL_OFFSET
    wall_end_x = x + house_width + WALL_OFFSET
    wall_end_z = z + house_length + WALL_OFFSET
    geo.placeCuboid(ED, (wall_start_x, AVGHEIGHT, wall_start_z), (wall_end_x, y + 2, wall_start_z), WALL_BLOCK, )
    # North wall
    geo.placeCuboid(ED,(wall_start_x, AVGHEIGHT, wall_end_z),(wall_end_x, y + 2, wall_end_z),WALL_BLOCK,)  # South wall
    geo.placeCuboid(ED,(wall_start_x, AVGHEIGHT, wall_start_z),(wall_start_x, y + 2, wall_end_z),WALL_BLOCK,)
    # West wall
    geo.placeCuboid(ED,(wall_end_x, AVGHEIGHT, wall_start_z),(wall_end_x, y + 2, wall_end_z),WALL_BLOCK,)
    # East wall
    # === Add Spanish-Style Gate to West Wall ===
    logging.info("Adding Spanish-style decorative gate on west side...")
    # Define the gate position on the west compound wall
    gate_z_start = wall_start_z + (wall_end_z - wall_start_z) // 2 - 1
    gate_z_end = gate_z_start + 3  # Wider gate for the wider pathway
    for gz in range(gate_z_start, gate_z_end + 1):
        geo.placeCuboid(
            ED,(wall_start_x, AVGHEIGHT, gz),(wall_start_x, AVGHEIGHT + 2, gz),Block("dark_oak_fence"))# Decorative fence blocks for the gate
    # Create open space (air blocks) for the gate entry
    geo.placeCuboid(
        ED,(wall_start_x, AVGHEIGHT, gate_z_start),(wall_start_x, AVGHEIGHT + 1, gate_z_end),Block("air"))
    logging.info("Spanish-style gate added to the west wall.")
     # === Interior Lighting to Prevent Bat Spawning ===
    for lantern_x in range(x + 1, x + 14, 3):  # Place lanterns every 3 blocks
        for lantern_z in range(z + 1, z + 19, 3):
            ED.placeBlock((lantern_x, y + 5, lantern_z), LIGHT_BLOCK)  # Ceiling lighting
    logging.info("Interior lighting added to prevent bats from spawning.")
    # === Compound Light Sources ===
    for wall_z in range(wall_start_z, wall_end_z + 1, 10):  # Spaced every 10 blocks
        ED.placeBlock((wall_start_x, y + 3, wall_z), LIGHT_BLOCK)  # West wall
        ED.placeBlock((wall_end_x, y + 3, wall_z), LIGHT_BLOCK)  # East wall

    for wall_x in range(wall_start_x, wall_end_x + 1, 10):
        ED.placeBlock((wall_x, y + 3, wall_start_z), LIGHT_BLOCK)  # North wall
        ED.placeBlock((wall_x, y + 3, wall_end_z), LIGHT_BLOCK)  # South wall
    logging.info("Exterior lighting added to compound walls to prevent bats.")
    # === Fill Hollow Spaces ===
    geo.placeCuboid(
        ED,(x + 1, y + 5, z + 1),(x + 14, y + 6, z + 19), Block("stone"))# Fill roof with stone or another solid block
    logging.info("Potential hollow spaces inside the house filled.")
    # === Pathway from West Gate to Living Room Door ===
    logging.info("Adding wider pathway from the west gate to the living room door...")
    path_block_primary = Block("terracotta")
    path_block_secondary = Block("polished_andesite")
    garden_block = Block("grass_block")  # Base for plants
    flower_blocks = [Block("rose_bush"), Block("peony"), Block("sunflower")]  # Decorative plants
    path_width = 4  # Wider pathway
    # Horizontal pathway segment from west gate towards the front of the house
    gate_mid_z = (gate_z_start + gate_z_end) // 2  # Midpoint of the gate
    for px in range(wall_start_x + 1, x):  # Path from west gate inward
        for pz in range(gate_mid_z - path_width // 2, gate_mid_z + path_width // 2):
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
            # Add garden rows along the sides of the pathway
            ED.placeBlock((px, y, gate_mid_z - path_width // 2 - 1), garden_block)
            ED.placeBlock((px, y, gate_mid_z + path_width // 2), garden_block)
            if px % 3 == 0:  # Place flowers every 3 blocks
                ED.placeBlock((px, y + 1, gate_mid_z - path_width // 2 - 1), (flower_blocks))
                ED.placeBlock((px, y + 1, gate_mid_z + path_width // 2), (flower_blocks))
    # Vertical pathway segment connecting to the front door
    for pz in range(gate_mid_z - path_width // 2, gate_mid_z + path_width // 2):
        for px in range(x, x + 1):  # Align to the front door
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
    logging.info("Wider pathway from west gate to living room door completed.")
     # === Add Spanish-Style Pathway Around the House ===
    logging.info("Adding Spanish-style path around the house...")
    # Redefine path width for around-the-house path
    path_block_primary = Block("terracotta")
    path_block_secondary = Block("polished_andesite")
    path_width = 2  # Around-path width is narrower
    # Front path (North side)
    for px in range(x - path_width, x + 16 + path_width):
        for pz in range(z - path_width, z):
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
    # Back path (South side)
    for px in range(x - path_width, x + 16 + path_width):
        for pz in range(z + 21, z + 21 + path_width):
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
    # Left path (West side)
    for pz in range(z - path_width, z + 21 + path_width):
        for px in range(x - path_width, x):
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
    # Right path (East side)
    for pz in range(z - path_width, z + 21 + path_width):
        for px in range(x + 16, x + 16 + path_width):
            block = path_block_primary if (px + pz) % 2 == 0 else path_block_secondary
            ED.placeBlock((px, y, pz), block)
    logging.info("Spanish-style path around the house completed!")
    logging.info("House and surrounding pathway completed!")


def decorateInterior(x, z):
    y = AVGHEIGHT
    # === Place the bed ===
    compass = ["east", "west", "north", "south"]
    facing = random.choice(compass)
    bed = ["red_bed", "green_bed", "blue_bed"]
    bed_type = random.choice(bed)
    ED.placeBlock((x + 5, y + 1, z + 2), Block(bed_type, {"facing": facing, "part": "foot"}))
    ED.placeBlock((x + 5, y + 1, z + 3), Block("", {"facing": facing, "part": "head"}))
    # === Place the bookshelf ===
    for bookshelf_y in range(y + 1, y + 4):
        for bookshelf_z in range(z + 5, z + 8):
            ED.placeBlock((x + 1, bookshelf_y, bookshelf_z), BOOKSHELF_BLOCK)
    for bookshelf_y in range(y + 1, y + 4):
        for bookshelf_z in range(z + 3, z + 4):
            ED.placeBlock((x + 8, bookshelf_y, bookshelf_z), BOOKSHELF_BLOCK)

    for bookshelf_y in range(y + 1, y + 4):
        for bookshelf_z in range(z + 14, z + 15):
            ED.placeBlock((x + 1, bookshelf_y, bookshelf_z+1), BOOKSHELF_BLOCK)
    for bookshelf_y in range(y + 1, y + 4):
          for bookshelf_z in range(z + 14, z + 15):
              ED.placeBlock((x + 8, bookshelf_y, bookshelf_z+3), BOOKSHELF_BLOCK)

    ED.placeBlock((x + 1, y + 3, z + 6), LIGHT_BLOCK)  # Near the bookshelf
    # === Add carpet to the floor ===
    carpet_colors = {0: Block("red_wool"), 1: Block("blue_wool"), 2: Block("green_wool"), 3: Block("yellow_wool")}
    carpet = random.choice(carpet_colors)
    for carpet_x in range(x + 1, x + 14):
        for carpet_z in range(z + 1, z + 19):
            # Exclude bed and bookshelf positions, as well as the table position (x + 6, z + 1)
            if (carpet_x == x + 5 and carpet_z in [z + 1, z + 2]) or \
                    (carpet_x == x + 1 and carpet_z in range(z + 5, z + 8)) or \
                    (carpet_x == x + 6 and carpet_z == z + 1):
                continue
            ED.placeBlock((carpet_x, y, carpet_z), carpet)
    # === Add windows on south and east walls ===
    # South wall windows (z-facing, opposite to the door)
    for window_z in range(z + 3, z + 20, 5):  # Add a window every 5 blocks
        ED.placeBlock((x + 15, y + 2, window_z), WINDOW_BLOCK)
        ED.placeBlock((x + 15, y + 3, window_z), WINDOW_BLOCK)
    # East wall windows (x-facing, overlooking east side)
    for window_x in range(x + 3, x + 15, 5):  # Add a window every 5 blocks
        ED.placeBlock((window_x, y + 2, z + 20), WINDOW_BLOCK)
        ED.placeBlock((window_x, y + 3, z + 20), WINDOW_BLOCK)
    # === Add windows on the west wall ===
    # West wall windows (x = start of the house, overlooking west side)
    for window_z in range(z + 3, z + 20, 5):  # Add a window every 5 blocks along the west wall
        if window_z in range(z + 5, z + 8):  # Bookshelf takes this segment
            continue
        ED.placeBlock((x, y + 2, window_z), WINDOW_BLOCK)
        ED.placeBlock((x, y + 3, window_z), WINDOW_BLOCK)


def buildRoof(x, z):
    y = AVGHEIGHT + 6
    roof_base_block = Block("terracotta")
    roof_edge_block = Block("brick_stairs")
    roof_height = 4
    house_width = 15
    house_length = 20
    for i in range(roof_height):
        # Calculate layer bounds and height
        layer_y = y + i
        layer_start_x, layer_end_x = x + i, x + house_width - i - 1
        layer_start_z, layer_end_z = z + i, z + house_length - i - 1
        # Place main roof layer
        geo.placeCuboid(ED,(layer_start_x, layer_y, layer_start_z),(layer_end_x, layer_y, layer_end_z),roof_base_block)
        # Place roof edges (skipping corners)
        # Handles all four edges (north, south, west, and east) in one pass
        for pos in range(layer_start_x + 1, layer_end_x):  # Horizontal edges (north and south)
            ED.placeBlock((pos, layer_y, layer_start_z), Block(roof_edge_block.id, {"facing": "north"}))  # North edge
            ED.placeBlock((pos, layer_y, layer_end_z), Block(roof_edge_block.id, {"facing": "south"}))  # South edge
        for pos in range(layer_start_z + 1, layer_end_z):  # Vertical edges (west and east)
            ED.placeBlock((layer_start_x, layer_y, pos), Block(roof_edge_block.id, {"facing": "west"}))  # West edge
            ED.placeBlock((layer_end_x, layer_y, pos), Block(roof_edge_block.id, {"facing": "east"}))  # East edge

    # Add ornamental top to finalize the roof design
    geo.placeCuboid(ED,(x + roof_height - 1, y + roof_height, z + roof_height - 1),(x + house_width - roof_height, y + roof_height, z + house_length - roof_height),roof_base_block)
    logging.info("Optimized Spanish-style roof with consolidated border logic completed!")

def buildSwimmingPool(center_x, center_z, orientation="horizontal"):
    logging.info("Building swimming pool...")
     # Swimming pool configuration
    POOL_LENGTH = 15  # Keep original length
    POOL_WIDTH = 10  # Updated to match the house's width (15 blocks)
    POOL_DEPTH = 4
    POOL_FLOOR_BLOCK = Block("polished_diorite")
    POOL_WALL_BLOCK = Block("quartz_block")
    WATER_BLOCK = Block("water")
    DECORATION_BLOCKS = [Block("sea_lantern"), Block("glowstone")]  # Underwater lighting
    # Determine pool position and orientation
    pool_y = AVGHEIGHT  # Use previously determined terrain height
    if orientation == "horizontal":
        # Horizontal orientation (along the X-axis)
        pool_x = center_x + 20  # Place pool to the right of the house
        pool_z = center_z + 5  # Center it along the Z-axis
        pool_start = (pool_x, pool_y - POOL_DEPTH, pool_z)
        pool_end = (pool_x + POOL_LENGTH, pool_y, pool_z + POOL_WIDTH)
    elif orientation == "vertical":
        # Vertical orientation (along the Z-axis)
        pool_x = center_x + 5  # Offset to align it behind the house
        pool_z = center_z + 25  # Place pool behind the house
        pool_start = (pool_x, pool_y - POOL_DEPTH, pool_z)
        pool_end = (pool_x + POOL_WIDTH, pool_y, pool_z + POOL_LENGTH)
    else:
        logging.error("Invalid orientation! Choose 'horizontal' or 'vertical'.")
        return
    # === Dig the pool area ===
    geo.placeCuboid(ED, pool_start, pool_end, Block("air"))
    # === Build pool floor ===
    geo.placeCuboid(ED, (pool_start[0], pool_y - POOL_DEPTH, pool_start[2]),
                    (pool_end[0], pool_y - POOL_DEPTH, pool_end[2]),
                    POOL_FLOOR_BLOCK)
    # === Build pool walls ===
    geo.placeCuboidHollow(ED, pool_start, pool_end, POOL_WALL_BLOCK)
    # === Fill with water ===
    geo.placeCuboid(ED, (pool_start[0] + 1, pool_y - POOL_DEPTH + 1, pool_start[2] + 1),
                    (pool_end[0] - 1, pool_y, pool_end[2] - 1),
                    WATER_BLOCK)
    # === Add underwater lighting ===
    lighting_corners = [
        (pool_start[0] + 1, pool_y - POOL_DEPTH + 1, pool_start[2] + 1),
        (pool_end[0] - 1, pool_y - POOL_DEPTH + 1, pool_end[2] - 1),
    ]
    for corner in lighting_corners:
        ED.placeBlock(corner, (DECORATION_BLOCKS))

    logging.info(f"Swimming pool ({orientation}) completed!")

def addRooms(x, z):
    """
    Adds rooms into the house by placing interior walls, doors, and lighting.
    Includes doors on the left and right sides of the corridor for Bedroom and other rooms.
    """
    y = AVGHEIGHT
    # === Add Interior Walls ===
    logging.info("Adding interior walls to create rooms...")
    # Horizontal divider walls with gaps for entrances
    geo.placeCuboid(ED, (x + 1, y, z + 7), (x + 3, y + 5, z + 7),
                    WALL_BLOCK)  # Left part of the wall (Living Room <-> Corridor) with a hole
    geo.placeCuboid(ED, (x + 2, y, z + 7), (x + 4, y + 5, z + 7),
                    WALL_BLOCK)  # Left part of the wall continues after the hole
    geo.placeCuboid(ED, (x + 8, y, z + 7), (x + 14, y + 5, z + 7),
                    WALL_BLOCK)  # Right part of the wall (Corridor <-> Bedroom)
    geo.placeCuboid(ED, (x + 1, y, z + 12), (x + 6, y + 5, z + 12),
                    WALL_BLOCK)  # Left part of the wall (Bedroom <-> Corridor)
    geo.placeCuboid(ED, (x + 2, y + 1, z + 12), (x + 3, y + 3, z + 12), Block("air"))

    geo.placeCuboid(ED, (x + 8, y, z + 12), (x + 14, y + 5, z + 12),
                    WALL_BLOCK)  # Right part of the wall (Corridor <-> Kitchen)
    # # Vertical divider wall with gaps for entrances
    geo.placeCuboid(ED, (x + 7, y, z + 1), (x + 7, y + 5, z + 4), WALL_BLOCK)  # Left-top wall (Living Room)
    geo.placeCuboid(ED, (x + 7, y, z + 6), (x + 7, y + 5, z + 10), WALL_BLOCK)  # Middle wall divider
    geo.placeCuboid(ED, (x + 7, y, z + 11), (x + 7, y + 5, z + 19), WALL_BLOCK)  # Right-bottom wall (Kitchen)
    logging.info("Interior walls added with gaps for entrances and corridors.")
    # === Adding Entrances to Rooms ===
    logging.info("Adding doors and entrances to rooms...")
    # Living Room entrances
    ED.placeBlock((x + 7, y + 1, z + 5), DOOR_BLOCK)  # Door between Living Room and Corridor
    # Bedroom entrances
    ED.placeBlock((x + 7, y + 1, z + 10), DOOR_BLOCK)  # Door between Bedroom and Corridor
    # Kitchen entrances
    ED.placeBlock((x + 7, y + 1, z + 15), DOOR_BLOCK)  # Door between Kitchen and Corridor
    # Backdoor to swimming pool (from kitchen)
    geo.placeCuboid(ED, (x + 10, y, z + 19), (x + 11, y + 3, z + 19), Block("air"))  # Gap for door
    ED.placeBlock((x + 10, y + 1, z + 19), DOOR_BLOCK)  # Door from Kitchen to Swimming Pool
    logging.info("Doors added to Bedroom, Kitchen, and backdoor to swimming pool.")
    # === Add Lighting to Rooms ===
    logging.info("Adding lighting to rooms...")
    # Living Room lighting
    for lx, lz in [(x + 3, z + 3), (x + 5, z + 5)]:
        ED.placeBlock((lx, y + 4, lz), LIGHT_BLOCK)
    # Bedroom lighting
    for bx, bz in [(x + 9, z + 3), (x + 11, z + 6)]:
        ED.placeBlock((bx, y + 4, bz), LIGHT_BLOCK)
    # Kitchen lighting
    for kx, kz in [(x + 10, z + 15), (x + 12, z + 18)]:
        ED.placeBlock((kx, y + 4, kz), LIGHT_BLOCK)
    # Corridor lighting
    for cx, cz in [(x + 7, z + 4), (x + 7, z + 9), (x + 7, z + 14)]:
        ED.placeBlock((cx, y + 4, cz), LIGHT_BLOCK)
    logging.info("Lighting placed in all rooms and corridor.")

def buildVilla():
    """
    Main entry point for building the house and its surroundings.
    """
    try:
        scanTerrain()  # Analyze terrain and determine average height
        # Determine house center
        center_x = STARTX + (LASTX - STARTX) // 2
        center_z = STARTZ + (LASTZ - STARTZ) // 2
        # Build house (and compound wall, gate, and pathway)
        buildHouse(center_x, center_z)
        # Add interior decorations
        decorateInterior(center_x, center_z)
        # Add roof
        buildRoof(center_x, center_z)
        addRooms(center_x, center_z)
        # Build swimming pool
        buildSwimmingPool(center_x, center_z, orientation="horizontal")
        logging.info("Villa construction complete!")
    except Exception as e:
        logging.error(f"Error during villa construction: {e}")

if __name__ == "__main__":
    buildVilla()
