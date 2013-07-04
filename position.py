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

	def advance_same_line(self, n):
		'''
		Return a Position object that is offset from self by n characters. No line
		breaks occur.
		'''
		return Position(
				self.path, 
				self.char+n, 
				self.line, 
				self.column+n)

	def next_char_new_line(self):
		'''
		Return a Position object that is offset from self by one line break
		character.
		'''
		return Position(
				self.path, 
				self.char+1, 
				self.line+1, 
				1)
	
	def pretty(self):
		'''
		Return a pretty, human-readable string for this Position.
		'''
		return self.path + ", ligne " + str(self.line) + ", colonne " + str(self.column)
