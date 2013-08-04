def format_tree(top_level):
	padding = 0
	for x in (str(top_level)).split("\n"):
		start = 0
		if x[0] == '[':
			start = 1
			padding += 1
		elif x[0] == ']':
			start = 1
			padding -= 1
		elif x[0] == ',':
			start = 2
		for i in range(0, padding):
			print ("|   ", end='')
		print (x[start:])

