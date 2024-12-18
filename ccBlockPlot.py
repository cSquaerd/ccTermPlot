#!/bin/python3

import os, sys
import argparse
import subprocess
import numpy as np

# for bright, add 6 if ok
colors_websafe = {
	"violet": 55, # bright ok
	"purple": 93, # bright ok
	"pink": 201, # bright ok
	"red": 196, # bright ok
	"maroon": 52,
	"gold": 214, # bright ok
	"yellow": 226,
	"green": 46,
	"pine": 22, # bright ok
	"cyan": 51,
	"blue" : 21, # bright ok
	"navy" : 17, # bright ok
	"black": 232, # bright ok
	"gray": 239, # bright ok
	"white": 255
}
colors_nobright = set(["maroon", "green", "yellow", "cyan", "white"])
all_color_names = list(colors_websafe.keys()) + \
	list(map(lambda k : "bright_" + k, [k for k in colors_websafe.keys() if k not in colors_nobright]))

parser = argparse.ArgumentParser(
	description = "A bar plotter for up to two data streams", formatter_class = argparse.RawTextHelpFormatter
)

parser.add_argument("-C", "--charliesway", action = "store_true", help = "Shortcut for the flags -saltg (see below)")

parser_data = parser.add_argument_group("Data", "Arguments for handling data input")
parser_flags = parser.add_argument_group("Flags", "Boolean Arguments for specific adjustments to the plot")
parser_color = parser.add_argument_group("Color", "Arguments for adjusting color(s) in the plot")
parser_label = parser.add_argument_group("Label", "Arguments for adjusting labels around the plot")

parser_data.add_argument("-s", "--stdin", action = "store_true", help = "Read the data from stdin; Ideal for piping")

parser_data.add_argument(
	"-f", "--file", action = "store", metavar = "InputFile",
	help = (
		"Read the data from a file\n\nThe data should be either one number per line,\n"
		"or two numbers per line, separated by a comma;\nSpace & Tab separation also works instead of Lines"
	)
)
parser_data.add_argument(
	"-x", "--xlabels", action = "store_true",
	help = "First column of data contains labels;\nWorks in single or double data modes"
)

parser_data.add_argument(
	"-y0", "--ymin", action = "store", type = float, default = None, metavar = "YMin",
	help = "Y value that should be at the bottom of the plot;\nNo effect without --adjust"
)

parser_data.add_argument(
	"-yn", "--ymax", action = "store", type = float, default = None, metavar = "YMax",
	help = "Y value that should be at the top of the plot;\nNo effect without --adjust"
)

parser_flags.add_argument(
	"-l", "--limits", action = "store_true", help = "Write the axis limit values around\nthe corners of the plot"
)

parser_flags.add_argument(
	"-z", "--perzero", action = "store_true",
	help = "Draw the plot relative to the zero of the Y axis;\nPositive parts go up, negative parts go down"
)

parser_flags.add_argument(
	"-t", "--tick", action = "store_true",
	help = "Write tick values at every other text line\nalong the Y axis; No effect without --limits"
)

parser_flags.add_argument(
	"-a", "--adjust", "--scale", action = "store_true",
	help = "Transform the data to fit within your terminal\nautomatically; Y axis is scaled, X axis is truncated"
)

parser_flags.add_argument(
	"-g", "--grid", action = "store_true", help = "Draw a grid behind the data, defaults to 3 wide, 2 high"
)

parser_color.add_argument("-c", "--nocolor", action = "store_true", help = "Disable all color in the plot\n\n")

colors_per_line = 5
parser_color.add_argument(
	"-c1", "--color1", action = "store", metavar = "PrimaryColor", default = "bright_gold",
	help = "Set the primary color of the bars,\ndefaults to bright_gold"
)
parser_color.add_argument(
	"-c2", "--color2", action = "store", metavar = "AuxiliaryColor", default = "bright_pine",
	help = (
		"Set the auxiliary color (for Y2) of the bars,\ndefaults to bright_pine\n\n"
		"Colors to choose from are:\n* {:s}"
	).format(
		"\n* ".join(
			[
				", ".join(
					k for k in all_color_names[colors_per_line * i:colors_per_line * i + colors_per_line]
				)
				for i in range(int(np.ceil(len(all_color_names) / colors_per_line)))
			]
		)
	)
)

parser_label.add_argument("-x0", "--xmin", action = "store", metavar = "Minimum", help = "Minimum/Lefthand X axis label")
parser_label.add_argument(
	"-xn", "--xmax", action = "store", metavar = "Maximum",
	help = "Maximum/Righthand X axis label\n\nLabels are strings of at most twelve characters;\nNo effect without --limits"
)
parser_label.add_argument(
	"-gw", "--gridwidth", action = "store", metavar = "Width", type = int, default = 3,
	help = "Width of the background grid"
)
parser_label.add_argument(
	"-gh", "--gridheight", action = "store", metavar = "Height", type = int, default = 2,
	help = "Height of the background grid"
)

def blockplot(
	Y : np.array, X : np.array, Y2 : np.array = None, color1 : str = "bright_gold", color2 : str = "bright_pine",
	limits : bool = False, perzero : bool = False, tick : bool = False, nocolor : bool = False, grid : bool = False,
	x_limits : tuple = None, y_limits : tuple = None, y_extrema : tuple = None, grid_dims : tuple = (3, 2)
) -> str:
	"""
	Given a list of X values and one or two equally-sized lists of Y values, produce a bar plot of the data;
	Optionally, color the data, add scale tick labels on both axes, override said labels, draw a background grid,
	and/or draw the data originating from the X axis (Y = 0)
	"""

	try:
		color1_bright, color1_name = color1.split('_')
	except ValueError:
		color1_name = color1
		color1_bright = ""

	try:
		color2_bright, color2_name = color2.split('_')
	except ValueError:
		color2_name = color2
		color2_bright = ""

	if Y.ndim != 1 or X.ndim != 1 or (Y2 is not None and Y2.ndim != 1):
		return "Inputs are not one-dimensional"
	elif Y.size != X.size or (Y2 is not None and Y2.size != X.size):
		return "Inputs are not the same size"
	elif color1_name not in colors_websafe.keys() or color2_name not in colors_websafe.keys():
		return "Invalid color(s) specified"

	if Y2 is not None:
		double_mode = True
	else:
		double_mode = False

	color1 = colors_websafe[color1_name]
	if color1_bright == "bright" and color1_name not in colors_nobright:
		color1 += 6
	color2 = colors_websafe[color2_name]
	if color2_bright == "bright" and color2_name not in colors_nobright:
		color2 += 6

	color1_prefix = "\x1B[38;5;{:d}m".format(color1)
	color2_prefix = "\x1B[38;5;{:d}m".format(color2)
	if nocolor:
		color1_prefix = ""
		color2_prefix = ""
	
	colors = (color1_prefix, color2_prefix)
	
	color1_to_2 = "\x1B[38;5;{:d};48;5;{:d}m".format(color1, color2)
	color2_to_1 = "\x1B[38;5;{:d};48;5;{:d}m".format(color2, color1)
	if nocolor:
		color1_to_2 = ""
		color2_to_1 = ""
	
	color_changes = (color1_to_2, color2_to_1) # index with smaller
	
	color_clear = "\x1B[0m"
	color_reverse = "\x1B[7m"

	if y_extrema is not None:
		ymin, ymax = y_extrema
	elif double_mode:
		ymin = min(np.min(Y), np.min(Y2))
		ymax = max(np.max(Y), np.max(Y2))
	else:
		ymin = np.min(Y)
		ymax = np.max(Y)

	if perzero:
		yrange = np.max(np.array([ymax - 0., ymax - ymin, 0. - ymin]))
	else:
		yrange = ymax - ymin
		Y -= ymin # Move these subtracrtions onto T
		if double_mode:
			Y2 -= ymin

	assert np.round(yrange, 3) != 0.

	if grid:
		w = grid_dims[0]
		h = grid_dims[1]

		background = lambda x, y: (
			' ' if x % w != w - 1 and y % h != h - 1 else
			'-' if x % w != w - 1 else
			'|' if y % h != h - 1 else
			'+'
		)
	else:
		background = lambda x, y : ' '

	blocks = [[background(x, y) for x in range(X.size)] for y in range(round(yrange))]
	chars = ' ' + ''.join([chr(c) for c in range(0x2581, 0x2588)])

	if double_mode:
		T = np.vstack((np.copy(Y), np.copy(Y2)))
		smaller = (T[0] > T[1]).astype(int)
		bigger = (T[1] >= T[0]).astype(int)
	else:
		T = np.copy(Y)

	# Setting the two ranges depending on mode here allows for no code copying
	if perzero:
		range_top = range(max(round(ymax), 0) - 1, -1, -1)
	else:
		range_top = range(len(blocks) - 1, -1, -1)
	
	for y in range_top:
		for x in range(X.size):
			if double_mode:
				i = smaller[x]
				j = bigger[x]

				if T[i, x] >= 1. and T[j, x] >= 1.: # smaller and bigger not at edge yet
					blocks[y][x] = colors[i] + '\u2588' + color_clear
					T[i, x] -= 1.
					T[j, x] -= 1.
				elif T[i, x] >= 0. and T[j, x] >= 0.625: # smaller at edge, bigger strictly above half, possibly not done
					blocks[y][x] = color_changes[i] + chars[int(8 * T[i, x])] + color_clear
					T[i, x] = float("NaN")
					if T[j, x] >= 1.:
						T[j, x] -= 1.
					else:
						T[j, x] = float("NaN")
				elif T[i, x] >= 0.: # smaller and bigger at edges, bigger at half or below
					blocks[y][x] = colors[i] + chars[int(8 * T[i, x])] + color_clear
					T[i, x] = float("NaN")
					T[j, x] = float("NaN")
				elif T[j, x] >= 1.: # bigger not at edge yet
					blocks[y][x] = colors[j] + '\u2588' + color_clear
					T[j, x] -= 1
				elif T[j, x] >= 0: # bigger at edge alone
					blocks[y][x] = colors[j] + chars[int(8 * T[j, x])] + color_clear
					T[j, x] = float("NaN")
					
			else:
				if T[x] >= 1.:
					blocks[y][x] = color1_prefix + '\u2588' + color_clear
					T[x] -= 1.
				elif T[x] >= 0.:
					blocks[y][x] = color1_prefix + chars[int(8 * T[x])] + color_clear
					T[x] = float("NaN")
	
	for y in range(max(round(ymax), 0), len(blocks)):
		if not perzero:
			continue # Skips the inner loop if we are not in perzero mode

		for x in range(X.size):
			if double_mode:
				# Note since were on the negative side, bigger is more positive, smaller is more negative,
				# hence smaller Is bigger ;)
				i = bigger[x]
				j = smaller[x]

				if T[i, x] <= -1. and T[j, x] <= -1.: # smaller and bigger not at edge yet
					blocks[y][x] = colors[i] + '\u2588' + color_clear
					T[i, x] += 1.
					T[j, x] += 1.
				elif T[i, x] <= 0. and T[j, x] <= -0.625: # smaller at edge, bigger strictly below half, possibly not done
					blocks[y][x] = color_reverse + color_changes[i] + chars[7 + int(8 * T[i, x])] + color_clear
					T[i, x] = float("NaN")
					if T[j, x] <= -1.:
						T[j, x] += 1.
					else:
						T[j, x] = float("NaN")
				elif T[i, x] <= 0.: # smaller and bigger at edges, bigger at half or above
					blocks[y][x] = color_reverse + colors[i] + chars[7 + int(8 * T[i, x])] + color_clear
					T[i, x] = float("NaN")
					T[j, x] = float("NaN")
				elif T[j, x] <= -1.: # bigger not at edge yet
					blocks[y][x] = colors[j] + '\u2588' + color_clear
					T[j, x] += 1
				elif T[j, x] <= 0: # bigger at edge alone
					blocks[y][x] = color_reverse + colors[j] + chars[7 + int(8 * T[j, x])] + color_clear
					T[j, x] = float("NaN")
					
			else:
				if T[x] <= -1.:
					blocks[y][x] = color1_prefix + '\u2588' + color_clear
					T[x] += 1.
				elif T[x] <= 0.:
					blocks[y][x] = color_reverse + color1_prefix + chars[7 - int(8 * T[x] * -1)] + color_clear
					T[x] = float("NaN")
	
	if limits:
		for i in range(round(yrange)):
			blocks[i].insert(0, ' ' * 8)

		y_limits_override = False
		if y_limits is not None and len(y_limits) == 2:
			blocks[0][0] = "{: ^7.2F} ".format(y_limits[1])
			blocks[-1][0] = "{: ^7.2F} ".format(y_limits[0])
			y_limits_override = True
		elif perzero and not tick:
			blocks[0][0] = "{: ^7.2F} ".format(max(ymax, 0.))
			blocks[-1][0] = "{: ^7.2F} ".format(min(ymin, 0.))
		elif not tick:
			blocks[0][0] = "{: ^7.2F} ".format(ymax)
			blocks[-1][0] = "{: ^7.2F} ".format(ymin)

		if tick:
			height = len(blocks)
			if y_limits_override:
				ticks = np.linspace(y_limits[0], y_limits[1], height)
			elif perzero:
				ticks = np.linspace(min(ymin, 0.), max(ymax, 0.), height)
			else:
				ticks = np.linspace(ymin, ymax, height)

			start, end = (2, height - 2) if y_limits_override else (0, height)
			for i in range(start, end, 2):
				blocks[i][0] =  "{: ^7.2F} ".format(ticks[height - 1 - i])
		
		blocks.append(
			[' ' * 8, "{: <11.2F} ".format(np.min(X)), ' ' * max(X.size - 24, 0), " {: >11.2F}".format(np.max(X))]
		)
		if x_limits is not None and len(x_limits) == 2:
			blocks[-1][1] = "{: <12s}".format(x_limits[0][:12])
			blocks[-1][3] = "{: >12s}".format(x_limits[1][:12])
	
	return '\n'.join([''.join([char for char in line]) for line in blocks])

if __name__ == "__main__":
	argV = parser.parse_args()
	#print(argV)

	if argV.charliesway:
		argV.stdin = True
		argV.adjust = True
		argV.limits = True
		argV.tick = True
		argV.grid = True

	if not argV.stdin and argV.file is None:
		print("Error: No input method provided. Exiting...")
		exit(1)
	
	if argV.stdin:
		raw = sys.stdin.read()
	else:
		with open(argV.file, 'r') as f:
			raw = f.read()

	try:
		lines = [s for s in raw.split() if len(s) > 0]
		if len(lines) == 0:
			print("Error: No lines found on stdin. Exiting...")
			exit(1)

		if ',' in lines[0]:
			comma_count = lines[0].count(',')

			x_labels = None
			i1 = 0
			i2 = 1
			if argV.xlabels:
				x_labels = list(map(lambda s : s.split(',')[0], lines))
				i1 = 1
				i2 = 2

			Y = np.array(list( map(lambda s : float(s.split(',')[i1]), lines) ))
			if comma_count == 1 and not argV.xlabels or comma_count == 2 and argV.xlabels:
				Y2 = np.array(list( map(lambda s : float(s.split(',')[i2]), lines) ))
		else:
			Y = np.array(list( map(lambda s : float(s), lines) ))
			Y2 = None

	except ValueError as ve:
		print("Error: Could not parse data: <Line {:s}: {:s}>".format(str(ve.__traceback__.tb_lineno), str(ve)))
		exit(2)
	except IndexError as ie:
		print(
			"Error: Found line with single value in double data mode: "
			"<Line {:s}: {:s}>".format(str(ie.__traceback__.tb_lineno), str(ie))
		)
		exit(2)

	#print(Y)
	#print(Y2)

	y_limits = None
	y_extrema = None

	if argV.adjust:
		columns, lines = os.get_terminal_size()

		if argV.limits: # Padding from tick labels
			columns -= 8
			lines -= 2 # one extra for the status line

		if Y2 is None:
			ymin = np.min(Y)
			ymax = np.max(Y)
		else:
			ymin = min(np.min(Y), np.min(Y2))
			ymax = max(np.max(Y), np.max(Y2))

		y_extrema_override = False

		if argV.ymin is not None:
			#Y += (ymin - argV.ymin)
			#if Y2 is not None:
			#	Y2 += (ymin - argV.ymin)
			ymin = argV.ymin
			y_extrema_override = True
		if argV.ymax is not None:
			ymax = argV.ymax
			y_extrema_override = True

		if argV.perzero:
			y_limits = (min(ymin, 0.), max(ymax, 0.)) # Computed before scaling
			yrange = max(np.array([ymax - 0., ymax - ymin, 0. - ymin]))
		else:
			y_limits = (ymin, ymax) # Computed before scaling
			yrange = ymax - ymin
	
		try:
			yscale = lines / yrange
		except ZeroDivisionError as ze:
			print(
				"Error: Range of Y values is zero, cannot scale data: "
				"<Line {:s}: {:s}>".format(str(ze.__traceback__.tb_lineno), str(ze))
			)
		
		if y_extrema_override:
			y_extrema = (ymin * yscale, ymax * yscale)

		Y = (yscale * Y)[:columns]
		if Y2 is not None:
			Y2 = (yscale * Y2)[:columns]

	X = np.arange(Y.size)
	x_limits = (argV.xmin, argV.xmax) if argV.xmin is not None and argV.xmax is not None else None
	if argV.xlabels:
		x_limits = (x_labels[0], x_labels[Y.size - 1])

	print(
		blockplot(
			Y, X, Y2 = Y2, x_limits = x_limits, y_limits = y_limits,
			limits = argV.limits, perzero = argV.perzero, tick = argV.tick, nocolor = argV.nocolor, grid = argV.grid,
			color1 = argV.color1, color2 = argV.color2, y_extrema = y_extrema, grid_dims = (argV.gridwidth, argV.gridheight)
		)
	)
