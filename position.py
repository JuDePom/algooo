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

	def pretty(self):
		'''
		Return a pretty, human-readable string for this Position.
		'''
		return self.path + ", ligne " + str(self.line) + ", colonne " + str(self.column)
