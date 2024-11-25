import numpy as np
def blockplot(Y : np.array, X : np.array, limits : bool = True, perzero : bool = False) -> str:
	if Y.ndim != 1 or X.ndim != 1:
		return "Inputs are not one-dimensional"
	elif Y.size != X.size:
		return "Inputs are not the same size"

	ymin = np.min(Y)
	ymax = np.max(Y)

	if perzero:
		yrange = np.max(np.array([ymax - 0., ymax - ymin, 0 - ymin]))
	else:
		yrange = ymax - ymin
		Y -= ymin

	assert np.round(yrange, 3) != 0.

	blocks = [[' ' for x in range(X.size)] for y in range(round(yrange))]
	chars = ' ' + ''.join([chr(c) for c in range(0x2581, 0x2588)])
	#print(chars)heroes

	T = np.copy(Y)

	if perzero:
		#print("top")
		for y in range(max(round(ymax), 0) - 1, -1, -1):
			#print(y)
			for x in range(X.size):
				if T[x] >= 1.:
					blocks[y][x] = '\u2588'
					T[x] -= 1.
				elif T[x] >= 0.:
					blocks[y][x] = chars[int(8 * T[x])]
					T[x] = float("NaN")
		#print("bottom")
		for y in range(max(round(ymax), 0), len(blocks)):
			#print(y)
			for x in range(X.size):
				if T[x] <= -1.:
					blocks[y][x] = '\u2588'
					T[x] += 1.
				elif T[x] <= 0.:
					blocks[y][x] = "\x1B[7m" + chars[7 - int(8 * T[x] * -1)] + "\x1B[0m"
					T[x] = float("NaN")
	else:
		for y in range(len(blocks) - 1, -1, -1):
			#print(y)
			for x in range(X.size):
				if T[x] >= 1.:
					blocks[y][x] = '\u2588'
					T[x] -= 1.
				elif T[x] >= 0.:
					#print(T[x])
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

	return '\n'.join([''.join([char for char in line]) for line in blocks])
