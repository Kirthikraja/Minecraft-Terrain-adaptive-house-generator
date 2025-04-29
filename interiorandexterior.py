import logging
from gdpc import Block, Editor,Box,Transform
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
from gdpc.geometry import placeBox, placeCheckeredBox
from gdpc.vector_tools import ivec3
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from termcolor import colored
import random
import numpy as np



from scipy.ndimage import uniform_filter, label

 
 # Set up logging
#logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.basicConfig(format=colored("%(name)s - %(levelname)s - %(message)s", color="yellow"))

# Initialize Editor object
ED = Editor(buffering=True)

# Define build area coordinates (modify as per your world slice)
BUILD_AREA = ED.getBuildArea()  
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

WORLDSLICE = ED.loadWorldSlice(BUILD_AREA.toRect(), cache=True)  # this takes a while

ROADHEIGHT = 0



def suitability_heatmap(x1, z1, x2, z2):
    """
    Generate a suitability heatmap for house placement based on terrain analysis.
    """
    

    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
   
    #  Determine the size of the area
    width, depth = x2 - x1 + 1, z2 - z1 + 1

    #  Directly Retrieve the Heighmap
    heights_fixed = np.maximum(heights, 1).astype(float)  # Ensure valid height values

    
    X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1), indexing='ij')  # Correct mapping

    #  Identify Water and Land (Low Suitability for Water)
    water_mask = (heights_fixed <= 63)   #this will exclude water
    suitability = np.ones_like(heights_fixed, dtype=float)  # Suitability starts at 1.0
    suitability[water_mask] = 0.0  # Set water areas to 0.0 immediately

    # 5️⃣ Calculate Flatness Using a Standard Deviation Filter
    height_variation = uniform_filter(heights_fixed, size=5, mode="reflect")
    flatness_score = 1 - (height_variation / np.max(height_variation))  # Normalize (Higher = More Flat)
    
    # Apply flatness to suitability map
    suitability *= flatness_score

    # 6️⃣ Identify the Largest Connected Stable Region for House Placement
    flat_mask = (height_variation <= np.mean(height_variation))  # Define "flat" as below mean variation
    labeled_areas, num_areas = label(flat_mask)
    largest_area = np.argmax(np.bincount(labeled_areas.flat)[1:]) + 1  # Find the largest connected flat area
    
    # Increase suitability for the largest stable area (Ensure a safe buildable region)
    suitability[labeled_areas == largest_area] *= 1.2  

    # 7️⃣ Re-Apply Water Mask (Ensure Water is Fully Removed)
    suitability[water_mask] = 0.0  

    # 8️⃣ Normalize Suitability Score for Better Visualization (Scale 0.8 to 1.0)
    min_suitability, max_suitability = np.min(suitability), np.max(suitability)
    if max_suitability > min_suitability:
        suitability = 0.8 + (suitability - min_suitability) / (max_suitability - min_suitability) * 0.2

    # 9️⃣ Plot the Corrected Suitability Heatmap Using the **Exact Mapping Like Scatter Plot**
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = plt.cm.hot  # Use "hot" colormap (black-red-yellow-white)
    img = ax.imshow(suitability, cmap=cmap, origin="lower", extent=[z1, z2+1, x1, x2+1])

    # Add colorbar
    plt.colorbar(img, label="Suitability Score (Higher is Better)")

    # Set labels and title
    ax.set_title(" Suitability  Heatmap ")
    ax.set_xlabel("Z  Coordinate")
    ax.set_ylabel("X  Coordinate")
    ax.set_aspect("equal", "box")

    # disclaimer text
    plt.figtext(0.5, 0.01, "Please close the heatmap to continue running the code.", ha="center", fontsize=10, color="red")

    plt.show()


def LandWaterheatmap(x1, z1, x2, z2):
    """
    Generate a heatmap differentiating land and water .
    
    """
   

    #  Determine the size of the area in blocks.
    # width = x2 - x1 + 1   #  blocks along the X-axis
    # depth = z2 - z1 + 1   #  blocks along the Z-axis

   
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    
    # Ensure all height values are at least 1
    heights = np.maximum(heights, 1)

     # Compute water/land classification using a vectorized condition.
    water = (heights.T <= 63)  # Adjusted threshold for water 
    
    #  heatmap: 1 for water, 0 for land.
    heatmap = np.where(water, 1, 0)

    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    #  blue for water (1), green for land (0).
    cmap = colors.ListedColormap(["green", "blue"])  
    bounds = [-0.5, 0.5, 1.5]  # Map values in [-0.5,0.5] to 0 and (0.5,1.5] to 1.
    norm = colors.BoundaryNorm(bounds, cmap.N)

    #  transposing the heatmap to alling it with the actual build area
    img = ax.imshow(heatmap.T, cmap=cmap, norm=norm,
                    origin="lower", extent=[z1, z2+1, x1, x2+1])

    # Adding grid line.
    ax.set_xticks(np.arange(z1, z2+2) - 0.5, minor=True)  # X-axis for  Z coordinate
    ax.set_yticks(np.arange(x1, x2+2) - 0.5, minor=True)  # Y-axis for X coordinate
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)

    # 7) Set titles and labels.
    ax.set_title(" Land-Water Heat Map ")
    ax.set_xlabel("Z coordinates")  # **X-axis now represents Z-coordinates**
    ax.set_ylabel("X coordinates")  # **Y-axis now represents X-coordinates**
    ax.set_aspect("equal", "box")

    # disclaimer
    plt.figtext(0.5, 0.01, "close the heatmap to continue running the code.", ha="center", fontsize=9, color="red")

    
    plt.show()  
    

    
def height_scatter_plot(x1, z1, x2, z2):
    """
    Generating a scatter plot ,which represent the train taking y coordinate 
    """

    

    heights = np.maximum(WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"], 1)  # Ensure valid heights

   
    X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1), indexing='ij')  # Match heatmap indexing
    
    #  Flatten the arrays for scatter plotting
    X_flat = X.flatten()
    Z_flat = Z.flatten()
    flatarea = heights.flatten()

    # 5) Create scatter plot of heights
    fig, ax = plt.subplots(figsize=(6, 6))
    scatter = ax.scatter(Z_flat, X_flat, c=flatarea, cmap="viridis", edgecolor='k', alpha=0.75)
    plt.colorbar(scatter, label="Height (Y-coordinates)")

    # 6) Set up axis labels and title
    ax.set_title("Scatter Plot ")
    ax.set_xlabel("Z coordinates")  # X-axis represents Z-coordinates
    ax.set_ylabel("X coordinates")  # Y-axis represents X-coordinates
    ax.set_aspect("equal", "box")
    ax.set_xlim([z1, z2+1])
    ax.set_ylim([x1, x2+1])  

    # Add disclaimer
    plt.figtext(0.5, 0.01, "close the heatmap to  run the code.", ha="center", fontsize=10, color="red")

    plt.show()
   
    
    

def buildHouse():

    x_center=PLATFORM_X
    z_center=PLATFORM_Z 
    y=ROADHEIGHT
    

    # Define house dimensions
    
    length = 8
    width = 8
    height = 6


    block_below = WORLDSLICE.getBlockGlobal(ivec3(x_center, y - 1, z_center))  # getting a block below from heightmaps

    below_str = str(block_below)  # Convert to a string 

    # Checking if it's a  water block
    if "water" in below_str.lower():  
        print("Water detected! ")
    else:
        print("Building house ..")
    
        

    

    # Create the foundation
        print("Building foundation...")
        geo.placeCuboid(ED, (x_center - length // 2, y, z_center - width // 2), 
                        (x_center + length // 2, y, z_center + width // 2), Block("stone_bricks"))

        # Create the cobblestone walls
        print("Building  walls...")
        geo.placeCuboid(ED, (x_center - length // 2, y + 1, z_center - width // 2), 
                        (x_center + length // 2, y + height, z_center - width // 2), Block("cobblestone"))
        geo.placeCuboid(ED, (x_center - length // 2, y + 1, z_center + width // 2), 
                        (x_center + length // 2, y + height, z_center + width // 2), Block("cobblestone"))
        geo.placeCuboid(ED, (x_center - length // 2, y + 1, z_center - width // 2), 
                        (x_center - length // 2, y + height, z_center + width // 2), Block("cobblestone"))
        geo.placeCuboid(ED, (x_center + length // 2, y + 1, z_center - width // 2), 
                        (x_center + length // 2, y + height, z_center + width // 2), Block("cobblestone"))
        

        # lantern poles 
        print("Adding lantern poles around the house...")
        lantern_pos = [
            (x_center - length // 2 - 2, y + 3, z_center - width // 2 - 2),
            (x_center + length // 2 + 2, y + 3, z_center - width // 2 - 2),
            (x_center - length // 2 - 2, y + 3, z_center + width // 2 + 2),
            (x_center + length // 2 + 2, y + 3, z_center + width // 2 + 2)
        ]
        for lantern_x, lantern_y, lantern_z in lantern_pos:
            geo.placeCuboid(ED, (lantern_x, y, lantern_z), (lantern_x, y + 3, lantern_z), Block("oak_fence"))
            ED.placeBlock((lantern_x, lantern_y, lantern_z), Block("lantern", {"hanging": "false"}))   

        # oak log beams 
        for dx in [-length // 2, length // 2]:
            for dz in [-width // 2, width // 2]:
                geo.placeCuboid(ED, (x_center + dx, y, z_center + dz), 
                                (x_center + dx, y + height, z_center + dz), Block("oak_planks"))

        # Building roof
        print("Building sharper triangular wooden roof...")
        for i in range(height // 2):
            geo.placeCuboid(ED, (x_center - length // 2 + i, y + height + i, z_center - width // 2 + i),
                            (x_center + length // 2 - i, y + height + i, z_center + width // 2 - i), Block("stone_bricks"))

        
        geo.placeCuboid(ED, (x_center - 1, y + height + height // 2, z_center - 1),
                        (x_center + 1, y + height + height // 2, z_center + 1), Block("stone_bricks"))
        

        #  glass window
        print("Adding a 2x3 glass window on one wall...")
        geo.placeCuboid(ED, (x_center - length // 2, y + 2, z_center),
                        (x_center - length // 2, y + 3, z_center + 2), Block("glass"))

        # working door
        print("Adding a working door...")
        ED.placeBlock((x_center, y + 1, z_center - width // 2), Block("oak_door", {"facing": "north", "half": "lower"}))
        ED.placeBlock((x_center, y + 2, z_center - width // 2), Block("oak_door", {"facing": "north", "half": "upper"}))

        

        # chimney
        print("Adding chimney...")
        chimney_x, chimney_z = x_center + length // 2 - 2, z_center
        geo.placeCuboid(ED, (chimney_x, y + height, chimney_z),
                        (chimney_x, y + height + 3, chimney_z), Block("bricks"))
        geo.placeCuboid(ED, (chimney_x, y + height + 4, chimney_z),
                        (chimney_x, y + height + 4, chimney_z), Block("campfire"))
        

         

            # Add chairs
        print("Adding chairs..")
        for dx in [-2, 2]:
            ED.placeBlock((x_center + dx, y + 1, z_center - width // 2 + 3), Block("oak_stairs", {"facing": "south"}))

        
        
        #Light
        print("Adding lighting...")
        using_torches = random.choice([True, False])  #

        if using_torches:
            for dz in [-width // 2 + 1, width // 2 - 1]:
                ED.placeBlock((x_center - length // 2 + 1, y + 3, z_center + dz), Block("wall_torch", {"facing": "east"}))
                ED.placeBlock((x_center + length // 2 - 1, y + 3, z_center + dz), Block("wall_torch", {"facing": "west"}))
        else:
            ED.placeBlock((x_center, y + height - 1, z_center), Block("lantern", {"hanging": "true"}))
            ED.placeBlock((x_center - 2, y + height - 1, z_center - 2), Block("lantern", {"hanging": "true"}))
            ED.placeBlock((x_center + 2, y + height - 1, z_center + 2), Block("lantern", {"hanging": "true"}))

    
    # carpet
    print("Adding carpet...")
    rug_colors = ["red_carpet", "blue_carpet", "green_carpet", "yellow_carpet"]#randomizing
    selected_carpet = random.choice(rug_colors)
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            ED.placeBlock((x_center + dx, y + 1, z_center + dz), Block(selected_carpet))

    # bed 
    print("Adding bed...")
    bed_sheet = ["red_bed", "blue_bed", "green_bed", "yellow_bed"]
    selected_bed = random.choice(bed_sheet)
    ED.placeBlock((x_center - 2, y + 1, z_center + width // 2 - 3), Block(selected_bed, {"facing": "south"}))
     
    


    # Add lantern poles in the lawn
    print("Adding lantern poles around the house...")
    lantern_pos = [
        (x_center - length // 2 - 2, y + 3, z_center - width // 2 - 2),
        (x_center + length // 2 + 2, y + 3, z_center - width // 2 - 2),
        (x_center - length // 2 - 2, y + 3, z_center + width // 2 + 2),
        (x_center + length // 2 + 2, y + 3, z_center + width // 2 + 2)
    ]
    for lantern_x, lantern_y, lantern_z in lantern_pos:
        geo.placeCuboid(ED, (lantern_x, y, lantern_z), (lantern_x, y + 3, lantern_z), Block("oak_fence"))
        ED.placeBlock((lantern_x, lantern_y, lantern_z), Block("lantern", {"hanging": "false"}))    



   #placing a person to guard a house
    print("guard inside the house...")
    
    guard_x, guard_y, guard_z = x_center, y + 1, z_center
    ED.runCommand(f"summon minecraft:villager {guard_x} {guard_y} {guard_z} {{CustomName:'\"Guard\"', VillagerData:{{profession:\"minecraft:weaponsmith\"}}}}")
    
    
        
    
    
    
def findingHeight():
    
    """in this function we determine the optimal height and its corresponding X ad Z value for the house platform"""

    global ROADHEIGHT, PLATFORM_X, PLATFORM_Z, PLATFORM_Y  # global variables

    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    print("Calculating house platform location...")

    #  Collect all land heights (exclude water, Y ≤ 63) *
    land_heights = []
    land_positions = {}  # Dictionary 


    for x in range(STARTX, LASTX + 1):
        for z in range(STARTZ, LASTZ + 1):
            h = heights[(x - STARTX, z - STARTZ)]
            if h > 63:  # **Exclude water (≤ 63)**
                land_heights.append(h)
                land_positions.setdefault(h, []).append((x, z))  # Store land positions

    #  Check **
    if not land_heights:
        print(" No land detected")
        PLATFORM_X, PLATFORM_Z, PLATFORM_Y = STARTX + (LASTX - STARTX) // 2, STARTZ + (LASTZ - STARTZ) // 2, 64
        return

    # Computing height differences**
    height_differences = [abs(land_heights[i] - land_heights[i + 1]) for i in range(len(land_heights) - 1)]

    # minimum meaningful gap dynamically**
    min_gap = min(height_differences) if height_differences else 1  # Use at least 1 if all heights are the same
    stable_threshold = min_gap + 1  # Allow minor variations

    #  longest stable height range based on the threshold**
    longest_start, longest_end = 0, 0
    current_start = 0

    for i in range(len(height_differences)):
        if height_differences[i] > stable_threshold:
            if (i - current_start) > (longest_end - longest_start):  # Check if this is the longest range so far
                longest_start, longest_end = current_start, i
            current_start = i + 1  # Start a new range

    # Finalizing
    if (len(height_differences) - current_start) > (longest_end - longest_start):
        longest_start, longest_end = current_start, len(height_differences)

    stable = land_heights[longest_start: longest_end + 1]
    
    #  Choose a representative height from the stable range**
    stable_height = int(np.median(stable))  # Pick the median for balance
    ROADHEIGHT = stable_height

    # Finding all  (X, Z) coordinates  within the median height **
    valid_positions = []
    for h in stable:
        valid_positions.extend(land_positions[h])

    #   random (X, Z) position in the stable range**
    import random
    best_x, best_z = random.choice(valid_positions)  #  random position 

    # Assign X, Z, Y to global variables and ensure house fits within**
    PLATFORM_X, PLATFORM_Z, PLATFORM_Y = best_x, best_z, stable_height

    print(f"Selected platform location: X={PLATFORM_X}, Z={PLATFORM_Z}, Y={PLATFORM_Y} (Stable ground )")




def buildGarden():

    xaxis=PLATFORM_X
    zaxis=PLATFORM_Z 
       
    y = ROADHEIGHT  
    platform_size = 25  # Size of the square platform


    
    
    
    block_below = WORLDSLICE.getBlockGlobal(ivec3(xaxis, y - 1, zaxis))  

    below_str = str(block_below)  # Convert to a string 

    # Check if it's water
    if "water" in below_str.lower():  # Convert to lowercase to avoid case issues
        print("Water detected! House placement canceled.")
    else:
        print("Building house on land...")
    
        


        def is_platform_supported(y_level):
            """Check if all four corners of the platform are touching solid ground."""
            corners = [
                (xaxis - platform_size // 2, y_level , zaxis - platform_size // 2),
                (xaxis - platform_size // 2, y_level , zaxis + platform_size // 2),
                (xaxis + platform_size // 2, y_level , zaxis - platform_size // 2),
                (xaxis + platform_size // 2, y_level , zaxis + platform_size // 2),
            ]
            unsupported_corners = 0

            for corner in corners:
                block_below = WORLDSLICE.getBlockGlobal(ivec3(*corner))
                block_below_str = str(block_below).lower()
                if block_below_str == "air" or "water" in block_below_str:
                    unsupported_corners += 1

            #  ALL corners are on solid ground
            return unsupported_corners == 0
           

        # Lower the platform if it's not
        while not is_platform_supported(y):
            y -= 1  # Move the platform down by 1
            print(f"Lowering platform to Y={y} for better support.")




        print("Building square platform ")
        
        # Clearing the area 
        geo.placeCuboid(ED, (xaxis - platform_size//2, y, zaxis - platform_size//2), 
                            (xaxis + platform_size//2, y + 10, zaxis + platform_size//2), Block("air"))
        
        #  Creating  land platform
        geo.placeCuboid(ED, (xaxis - platform_size//2, y, zaxis - platform_size//2), 
                            (xaxis + platform_size//2, y, zaxis + platform_size//2), Block("grass_block"))#glow-lichen
        
        
        
        
        # Adding  a fence 
        
        geo.placeCuboid(ED, (xaxis - platform_size//2, y + 1, zaxis + platform_size//2), 
                            (xaxis + platform_size//2, y + 1, zaxis + platform_size//2), Block("oak_fence"))
        geo.placeCuboid(ED, (xaxis - platform_size//2, y + 1, zaxis - platform_size//2), 
                            (xaxis - platform_size//2, y + 1, zaxis + platform_size//2), Block("oak_fence"))
        geo.placeCuboid(ED, (xaxis + platform_size//2, y + 1, zaxis - platform_size//2), 
                            (xaxis + platform_size//2, y + 1, zaxis + platform_size//2), Block("oak_fence"))
        
        # trees
        
        tree_spacing = 2  #
        inner_border = platform_size // 2 - 2  # Trees placed TWO blocks inside the fence

        for dx in range(-inner_border, inner_border + 1, tree_spacing):
            for dz in range(-inner_border, inner_border + 1, tree_spacing):
                # Only place trees inside
                if dx in {-inner_border, inner_border} or dz in {-inner_border, inner_border}:
                    if abs(dx) == inner_border and abs(dz) == inner_border:
                        continue  

                    

                    trunk_height = random.randint(4, 6)  # Randomize 

                    #  tree trunk
                    geo.placeCuboid(ED, (xaxis + dx, y + 1, zaxis + dz), 
                                        (xaxis + dx, y + trunk_height, zaxis + dz), Block("birch_log"))

                    #  leaf 
                    for i in range(-2, 3):
                        for j in range(-2, 3):
                            if abs(i) + abs(j) <= 3:  
                                geo.placeCuboid(ED, (xaxis + dx + i, y + trunk_height + 1, zaxis + dz + j), 
                                                    (xaxis + dx + i, y + trunk_height + 1, zaxis + dz + j), Block("oak_leaves"))

                    
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if abs(i) + abs(j) <= 2:
                                geo.placeCuboid(ED, (xaxis + dx + i, y + trunk_height + 2, zaxis + dz + j), 
                                                    (xaxis + dx + i, y + trunk_height + 2, zaxis + dz + j), Block("oak_leaves"))

                    
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if abs(i) + abs(j) <= 1:  
                                geo.placeCuboid(ED, (xaxis + dx + i, y + trunk_height + 3, zaxis + dz + j), 
                                                    (xaxis + dx + i, y + trunk_height + 3, zaxis + dz + j), Block("oak_leaves"))
        
        

                



def main():
    try:
       
        findingHeight()
        buildGarden()
        buildHouse()
        LandWaterheatmap(STARTX, STARTZ, LASTX, LASTZ)
        height_scatter_plot(STARTX, STARTZ, LASTX, LASTZ)
        suitability_heatmap(STARTX, STARTZ, LASTX, LASTZ)
        
        print("Done!")
    
    except KeyboardInterrupt: # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")

if __name__ == "__main__":
    main()