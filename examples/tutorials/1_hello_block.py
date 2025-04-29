#!/usr/bin/env python3

# ==============================================================================
#
# THE EXAMPLES ARE DEPRECATED!
#
# All in-repository examples are deprecated and will be removed in a future
# version of GDPC. They have been replaced by the new documentation website:
# https://gdpc.readthedocs.io/en/stable/.
#
# The examples are longer maintained and may be incompatible with the latest
# version of GDPC.
#
# ==============================================================================


"""
Place and retrieve a single block in the world.
"""

import sys

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)


# Place a block of red concrete at (0,80,0)!
editor.placeBlock((0,80,0), Block("red_concrete"))
editor.placeBlock((0,81,0), Block("prismarine")) #new
editor.placeBlock((0,79,0), Block("prismarine"))
editor.placeBlock((0,78,0), Block("prismarine"))
editor.placeBlock((0,76,0), Block("prismarine"))
editor.placeBlock((0,74,0), Block("prismarine"))

editor.placeBlock((0,73,0), Block("prismarine"))
editor.placeBlock((0,72,0), Block("prismarine"))
editor.placeBlock((0,71,0), Block("prismarine"))
editor.placeBlock((0,70,0), Block("prismarine"))


# Retrieve the block at (0,80,0) and print it.
block = editor.getBlock((0,80,0))
print(f"Block at (0,80,0): {block}")

block = editor.getBlock((0,81,0))
print(f"Block at (0,81,0): {block}") #new

block = editor.getBlock((0,79,0))
print(f"Block at (0,79,0): {block}") #new

block = editor.getBlock((0,78,0))
print(f"Block at (0,78,0): {block}") #new

block = editor.getBlock((0,76,0))
print(f"Block at (0,76,0): {block}") #new

block = editor.getBlock((0,75,0))
print(f"Block at (0,75,0): {block}") #new

block = editor.getBlock((0,74,0))
print(f"Block at (0,74,0): {block}") #new

block = editor.getBlock((0,73,0))
print(f"Block at (0,73,0): {block}") #new

block = editor.getBlock((0,72,0))
print(f"Block at (0,72,0): {block}") #new

block = editor.getBlock((0,71,0))
print(f"Block at (0,71,0): {block}") #new

block = editor.getBlock((0,70,0))
print(f"Block at (0,70,0): {block}") #new


# Tip: to get the ID of a block in Minecraft (like "red_concrete"), press F3 and point at the
# the block. The ID will be shown at the bottom right, below "Targeted Block". You can leave out the
# "minecraft:" part.
#
# To get the ID of a block in your inventory, you can also press F3 + H and then hover over the
# block. The ID should be shown at the bottom of the tooltip.
#
# You can also "delete" a block by placing Block("air") at its position.
