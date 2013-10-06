class Position(tuple):
	'''
	Position in an input LDA source code file.

	This class inherits from tuple, which makes it immutable.
	'''

	def __new__(cls, path, char=0, line=1, column=1):
		return tuple.__new__(cls, (path, char, line, column))

	def __init__(self, path, char=0, line=1, column=1):
		self.path = path
		self.char = char
		self.line = line
		self.column = column

	def __lt__(self, other):
		return self.path == other.path and self.char < other.char

	def __gt__(self, other):
		return self.path == other.path and self.char > other.char

	def __eq__(self, other):
		return self.path == other.path and self.char == other.char

	def __le__(self, other):
		return self.path == other.path and self.char <= other.char

	def __ge__(self, other):
		return self.path == other.path and self.char >= other.char

	def __repr__(self):
		return "{}:{}:{}".format(self.path, self.line, self.column)

	def pretty(self):
		'''
		Return a pretty, human-readable string for this Position.
		'''
		return "{}, ligne {}, colonne {}".format(self.path, self.line, self.column)

	def terse(self):
		return "{}:{}".format(self.line, self.column)

	def marker_lines(self, buf):
		prevcr = buf.rfind('\n', 0, self.char)
		nextcr = buf.find('\n', self.char)
		if nextcr == -1:
			nextcr = len(buf)
		line = buf[prevcr+1: nextcr]
		tick = ''
		for i in range(0, self.column-1):
			tick += '\t' if line[i] == '\t' else ' '
		tick += '^'
		return line, tick

