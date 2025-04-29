# Procedural House & Garden Generator (MGAIA Assignment 1)

This repository extends **GDPC** (Generative Design Python Client) to automatically analyze terrain in a Minecraft world slice, select a stable build platform, and procedurally generate a richly detailed house and garden—meeting the requirements of the MGAIA Assignment 1 at Leiden University (February 2025).

---

## Origins
This project is based on the [GDPC](https://github.com/avdstaaij/gdpc) framework by the GDMC community. We have forked and extended the original code to implement:

- Advanced terrain analysis and visualization (heatmaps, scatter plots).  
- Stable-platform selection via statistical filters and connected-area analysis.  
- Fully procedural garden and house construction with randomized variation.  

All original functionality and license terms from GDPC are retained (see [LICENSE](LICENSE)).

---

## Context & Requirements
** Procedural Content Generation ** tasked us with:

1. **Believable placement & terrain adaptation**:  
   • Analyze the selected build area (100×100 blocks).  
   • Identify a flattest, stable region above water level.  
   • Insert structures with minimal environmental disruption.

2. **House of specific architectural style**:  
   • An 8×8×6 cottage with stone-brick foundation, cobblestone walls, stepped roof, chimney, and oak-trim beams.  
   • Example style inspired by rustic medieval cottages.

3. **Interior & exterior decoration**:  
   • Interior: randomly colored carpet, bed, chairs.  
   • Exterior: oak fence, birch-tree garden, lantern poles, torches/hanging lanterns, guard villager.

4. **Procedural variation **:  
   • Randomized lantern styles, tree canopies, carpet/bed colors, chimney campfire, variation in garden tree positions.  
   • Every run produces a slightly different layout and color scheme.



---

## Features Overview
- **Terrain Analysis & Visualization**  
  - `LandWaterheatmap()`: land vs. water heatmap (green/blue).  
  - `height_scatter_plot()`: elevation scatter plot.  
  - `suitability_heatmap()`: “build suitability” heatmap excluding water and boosting largest flat region.

- **Platform Selection** (`findingHeight()`):  
  - Scans heightmap (Y > 63), excludes water, computes height variation, finds largest stable height band, picks median height and a random position within.

- **Garden Generation** (`buildGarden()`):  
  - Clears & levels 25×25 grass platform.  
  - Surrounds with oak-fence border.  
  - Plants birch trees with randomized trunk heights and layered oak-leaf canopies.  
  - Ensures all corners are on solid ground.

- **House Construction** (`buildHouse()`):  
  - Stone-brick foundation and walls, cobblestone walls, stone-stepped roof.  
  - Decorative elements: lantern poles, torches or hanging lanterns, oak beams, glass window, working oak door, chimney with campfire.  
  - Interior furniture: randomized carpet and bed colors, chairs, guard villager NPC.

- **Automation & Buffering**:  
  - Uses GDPC’s buffered `Editor` for efficient batch edits.  
  - Handles keyboard interrupt gracefully.

---