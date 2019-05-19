#!/usr/bin/env python

from __future__ import print_function

import re
import sys

from six.moves import input

filename = sys.argv[1]

layers = set()

with open(filename, 'r') as gcode:
    for line in gcode:
        if re.match(r";[\d\.\d]",line):
            layers.add(line.replace(";", "").strip())

layers_sorted = list(map(float, layers))
layers_sorted.sort()

# calculate layerheight
layer_count = len(layers_sorted)
layer_heights = []

previous_layer = layers_sorted[0]
for layer in layers_sorted[1:]:
    layer_heights.append(round(layer - previous_layer, 1))
    previous_layer = layer

layer_heights_set = set(layer_heights)
if len(layer_heights_set) > 1:
    print("Layer heights inconsistent")
    print(len(layer_heights_set))
    print(layer_heights_set)
    exit()

print("Layer height is:", layer_heights_set.pop())
print("Top layer is", max(layers_sorted))

print("How often would you like to switch colors?")
color_change_height = float(input("I want change to occur every (x) mm\n"))

layer_change_count = int(input("How many times would you like to switch color?\n"))


# select layers to switch on
layers_to_switch_on = []

for layer_switch in range(1, layer_change_count+1):
    previous_layer = layers_sorted[0]
    for layer in layers_sorted[1:]:
        if layer == round(layer_switch * color_change_height, 1):
            layers_to_switch_on.append(layer)
            break
        if layer > round(layer_switch * color_change_height, 1):
            layers_to_switch_on.append(previous_layer)
            break
        previous_layer = layer

print("Layers to switch on:", layers_to_switch_on)

color_change_lines = []
with open(filename, 'r') as original_gcode:
    with open("colored_" + filename, 'w') as new_gcode:
        last_layer_change = None
        line_counter = 0
        for original_line in original_gcode:
            line_counter+=1
            new_gcode.write(original_line)
            if re.match(r";[\d\.\d]",original_line):
                last_layer_change = float(original_line.replace(";", "").strip())
            if "; PURGING FINISHED" in original_line and last_layer_change in layers_to_switch_on:
                line_counter+=1
                new_gcode.write("M600\n")
                color_change_lines.append(line_counter)

print("color change added on lines", color_change_lines)
print("New file saved as:", "colored_" + filename)
