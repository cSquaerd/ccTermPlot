import numpy as np

def blockplot(
	Y : np.array, X : np.array, limits : bool = True, perzero : bool = False,
	x_limits : tuple = None, Y2 : np.array = None
) -> str:
	if Y.ndim != 1 or X.ndim != 1 or (Y2 is not None and Y2.ndim != 1):
		return "Inputs are not one-dimensional"
	elif Y.size != X.size or (Y2 is not None and Y2.size != X.size):
		return "Inputs are not the same size"

	if Y2 is not None:
		double_mode = True
	else:
		double_mode = False

	color1 = 21
	color2 = 93

	color1_prefix = "\x1B[38;5;{:d}m".format(color1)
	color2_prefix = "\x1B[38;5;{:d}m".format(color2)
	colors = (color1_prefix, color2_prefix)
	
	color1_to_2 = "\x1B[38;5;{:d};48;5;{:d}m".format(color1, color2)
	color2_to_1 = "\x1B[38;5;{:d};48;5;{:d}m".format(color2, color1)
	color_changes = (color1_to_2, color2_to_1) # index with smaller
	
	color_clear = "\x1B[0m"
	color_reverse = "\x1B[7m"

	if double_mode:
		ymin = min(np.min(Y), np.min(Y2))
		ymax = max(np.max(Y), np.max(Y2))
	else:
		ymin = np.min(Y)
		ymax = np.max(Y)

	if perzero:
		yrange = np.max(np.array([ymax - 0., ymax - ymin, 0 - ymin]))
	else:
		yrange = ymax - ymin
		Y -= ymin
		if double_mode:
			Y2 -= ymin

	assert np.round(yrange, 3) != 0.

	blocks = [[' ' for x in range(X.size)] for y in range(round(yrange))]
	chars = ' ' + ''.join([chr(c) for c in range(0x2581, 0x2588)])
	#print(chars)heroes

	if double_mode:
		T = np.vstack((np.copy(Y), np.copy(Y2)))
		smaller = (T[0] > T[1]).astype(int)
		bigger = (T[1] > T[0]).astype(int)
	else:
		T = np.copy(Y)

	if perzero:
		print("top")
		for y in range(max(round(ymax), 0) - 1, -1, -1):
			print(y)
			#if double_mode:
			#	print(T)

			for x in range(X.size):
				if double_mode:
					i = smaller[x]
					j = bigger[x]

					if T[i, x] >= 1. and T[j, x] >= 1.:
						blocks[y][x] = colors[i] + '\u2588' + color_clear
						T[i, x] -= 1.
						T[j, x] -= 1.
					elif T[i, x] >= 0. and T[j, x] >= 0.625:
						blocks[y][x] = color_changes[i] + chars[int(8 * T[i, x])] + color_clear
						T[i, x] = float("NaN")
						if T[j, x] >= 1.:
							T[j, x] -= 1.
						else:
							T[j, x] = float("NaN")
					elif T[i, x] >= 0.:
						blocks[y][x] = colors[i] + chars[int(8 * T[i, x])] + color_clear
						T[i, x] = float("NaN")
						T[j, x] = float("NaN")
					elif T[j, x] >= 1.:
						blocks[y][x] = colors[j] + '\u2588' + color_clear
						T[j, x] -= 1
					elif T[j, x] >= 0:
						blocks[y][x] = colors[j] + chars[int(8 * T[j, x])] + color_clear
						T[j, x] = float("NaN")

					
					"""
					print(x, T[i, x], T[j, x], end = "; ")
					if T[i, x] >= 1.:
						blocks[y][x] = colors[i] + '\u2588' + color_clear
						T[i, x] -= 1.
					elif T[i, x] >= 0.:
						if T[j, x] >= 0.625:
							change = color_changes[i]
							blocks[y][x] = change + chars[int(8 * T[i, x])] + color_clear
						else:
							blocks[y][x] = colors[i] + chars[int(8 * T[i, x])] + color_clear

						T[i, x] = float("NaN")
					
					elif T[j, x] >= 1.:
						blocks[y][x] = colors[j] + '\u2588' + color_clear
						T[j, x] -= 1.
					elif T[j, x] >= 0:
						blocks[y][x] = colors[j] + chars[int(8 * T[j, x])] + color_clear
						T[j, x] = float("NaN")
					
					#T[:, x] -= 1.
					"""
						
				else:
					if T[x] >= 1.:
						blocks[y][x] = '\u2588'
						T[x] -= 1.
					elif T[x] >= 0.:
						blocks[y][x] = chars[int(8 * T[x])]
						T[x] = float("NaN")
			#if double_mode:
			#	print(T)
		print("bottom")
		print(T)
		for y in range(max(round(ymax), 0), len(blocks)):
			print(y)
			for x in range(X.size):
				if double_mode:
					i = bigger[x]
					j = smaller[x]

					if T[i, x] <= -1. and T[j, x] <= -1.:
						blocks[y][x] = colors[i] + '\u2588' + color_clear
						T[i, x] += 1.
						T[j, x] += 1.
					elif T[i, x] <= 0. and T[j, x] <= -0.625:
						blocks[y][x] = color_reverse + color_changes[i] + chars[7 + int(8 * T[i, x])] + color_clear
						T[i, x] = float("NaN")
						if T[j, x] <= -1.:
							T[j, x] += 1.
						else:
							T[j, x] = float("NaN")
					elif T[i, x] <= 0.:
						blocks[y][x] = color_reverse + colors[i] + chars[7 + int(8 * T[i, x])] + color_clear
						T[i, x] = float("NaN")
						T[j, x] = float("NaN")
					elif T[j, x] <= -1.:
						blocks[y][x] = colors[j] + '\u2588' + color_clear
						T[j, x] += 1
					elif T[j, x] <= 0:
						blocks[y][x] = color_reverse + colors[j] + chars[7 + int(8 * T[j, x])] + color_clear
						T[j, x] = float("NaN")
						
				else:
					if T[x] <= -1.:
						blocks[y][x] = '\u2588'
						T[x] += 1.
					elif T[x] <= 0.:
						blocks[y][x] = color_reverse + chars[7 - int(8 * T[x] * -1)] + color_clear
						T[x] = float("NaN")
	else:
		for y in range(len(blocks) - 1, -1, -1):
			for x in range(X.size):
				if double_mode:
					i = smaller[x]
					j = bigger[x]
					
					#print(x, T[i, x], T[j, x], end = "; ")
					if T[i, x] >= 1.:
						blocks[y][x] = colors[i] + '\u2588' + color_clear
					elif T[i, x] >= 0.:
						if T[j, x] >= 0.625:
							change = color_changes[i]
							blocks[y][x] = change + chars[int(8 * T[i, x])] + color_clear
						else:
							blocks[y][x] = colors[i] + chars[int(8 * T[i, x])] + color_clear

						T[i, x] = float("NaN")
					elif T[j, x] >= 1.:
						blocks[y][x] = colors[j] + '\u2588' + color_clear
					elif T[j, x] >= 0:
						blocks[y][x] = colors[j] + chars[int(8 * T[j, x])] + color_clear
						T[:, x] = float("NaN")
					
					T[:, x] -= 1.
						
				else:
					if T[x] >= 1.:
						blocks[y][x] = '\u2588'
						T[x] -= 1.
					elif T[x] >= 0.:
						blocks[y][x] = chars[int(8 * T[x])]
						T[x] = float("NaN")
	
	if limits:
		for i in range(round(yrange)):
			blocks[i].insert(0, "        ")

		if perzero:
			blocks[0][0] = "{: ^7.2F} ".format(max(ymax, 0.))
			blocks[-1][0] = "{: ^7.2F} ".format(min(ymin, 0.))
		else:
			blocks[0][0] = "{: ^7.2F} ".format(ymax)
			blocks[-1][0] = "{: ^7.2F} ".format(ymin)
		
		blocks.append(
			["        ", "{: <7.2F} ".format(np.min(X)), ' ' * max(X.size - 16, 0), " {: >7.2F}".format(np.max(X))]
		)
		if x_limits is not None and len(x_limits) == 2:
			blocks[-1][1] = "{: <8s}".format(x_limits[0][:8])
			blocks[-1][3] = "{: >8s}".format(x_limits[1][:8])
	
	return '\n'.join([''.join([char for char in line]) for line in blocks])

