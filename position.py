# inherits from tuple to make it immutable
class Position(tuple):
	def __new__(cls, path, char=0, line=1, column=1):
		return tuple.__new__(cls, (path, char, line, column))

	def __init__(self, path, char=0, line=1, column=1):
		self.path = path
		self.char = char
		self.line = line
		self.column = column

	def advance_same_line(self, count):
		return Position(
				self.path, 
				self.char+count, 
				self.line, 
				self.column+count)

	def next_char_new_line(self):
		return Position(
				self.path, 
				self.char+1, 
				self.line+1, 
				1)
	
	def pretty(self):
		return self.path + ", ligne " + str(self.line) + ", colonne " + str(self.column
)
