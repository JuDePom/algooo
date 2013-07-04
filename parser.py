import keywords
import errors
from position import Position

def is_ident_char_1(c):
	'''
	Return True if c is a valid first character for an identifier.
	'''
	return c.isalpha() or c == '_'

def is_ident_char_2(c):
	'''
	Return True if c is a valid identifier character past the first character.
	'''
	return is_ident_char_1(c) or c.isnumeric()

class Parser:
	'''
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and True is returned;
	otherwise False is returned. These functions may raise an exception if a
	syntax error was found.
	'''

	def __init__(self, path):
		self.pos = Position(path)
		with open(path, 'r') as input_file:
			self.buf = input_file.read()

	def cc(self):
		'''
		Return the current character in the buffer.
		'''
		return self.buf[self.pos.char]

	def advance1(self):
		'''
		Advance current position in the buffer by one character and update self.pos
		accordingly.
		'''
		if self.cc() == '\n':
			self.pos = self.pos.next_char_new_line()
		else:
			self.pos = self.pos.advance_same_line(1)

	def advance_same_line(self, n):
		'''
		Advance current position in the buffer by n characters and update self.pos
		accordingly.
		'''
		self.pos = self.pos.advance_same_line(n)

	def analyze_raw(self, raw):
		'''
		Analyze a raw string at the current position.
		'''
		if self.buf.startswith(raw, self.pos.char):
			self.advance_same_line(len(raw))
			return True
		else:
			return False

	def analyze_raw_synonyms(self, synonyms):
		'''
		Analyze raw synonyms. That is, test for the presence of one of the
		raw synonyms in the list passed as a parameter.
		'''
		for raw in synonyms:
			if self.analyze_raw(raw):
				return True
		return False

	def skip_white(self):
		'''
		Skip any whitespace and comments starting at the current position and
		updates self.pos accordingly.
		'''
		state = 'WHITE'
		while state != 'END':
			if state is 'WHITE':
				# plain whitespace
				if self.cc().isspace():
					self.advance1()
				elif self.analyze_raw_synonyms(keywords.MULTILINE_COMMENT_START):
					state = 'MULTI'
				elif self.analyze_raw_synonyms(keywords.SINGLELINE_COMMENT_START):
					state = 'SINGLE'
				else:
					state = 'END'
			elif state is 'MULTI':
				# inside multi-line comment
				if self.analyze_raw_synonyms(keywords.MULTILINE_COMMENT_END):
					state = 'WHITE'
				else:
					self.advance1()
			elif state is 'SINGLE':
				# inside single-line comment
				if self.cc() == '\n':
					state = 'WHITE'
				self.advance1()

	def analyze_algorithm(self):
		'''
		Analyze an algorithm block.
		'''
		if not self.analyze_keyword(keywords.ALGORITHM):
			return False
		if not self.analyze_keyword(keywords.BEGIN):
			raise errors.ExpectedError(self.pos, keywords.BEGIN)
		while self.analyze_instruction():
# TODO !!! faire pour de vrai analyze_instruction()
			pass
		if not self.analyze_keyword(keywords.END):
			raise errors.ExpectedError(self.pos, keywords.END)

	def analyze_keyword(self, synonyms):
		'''
		Analyze a keyword (with synonyms).
		'''
		self.skip_white()
		for word in synonyms:
			before_word = self.pos
			if self.analyze_raw(word):
				if is_ident_char_2(self.cc()):
					# rewind
					self.pos = before_word
				else:
					self.advance1()
					return True
		return False

	def analyze_instruction(self):
		'''
		Analyze an instruction.
		'''
# TODO ! à implémenter !
		print ("TODO!!!")
		return False
