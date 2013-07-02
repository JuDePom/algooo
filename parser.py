import keywords
import errors
from position import Position

def is_ident_char_1(c):
	return c.isalpha() or c == '_'

def is_ident_char_2(c):
	return is_ident_char_1(c) or c.isnumeric()

class Parser:
	def __init__(self, path):
		self.pos = Position(path)
		with open(path, 'r') as input_file:
			self.buf = input_file.read()

	def cc(self):
		return self.buf[self.pos.char]

	def analyze_algorithm(self):
		if self.analyze_keyword(keywords.ALGORITHM):
			if not self.analyze_keyword(keywords.BEGIN):
				raise errors.ExpectedError(self.pos, keywords.BEGIN)
			while self.analyze_instruction():
# TODO !!! faire pour de vrai analyze_instruction()
				pass
			if not self.analyze_keyword(keywords.END):
				raise errors.ExpectedError(self.pos, keywords.END)

	def advance1(self):
		if self.cc() == '\n':
			self.pos = self.pos.next_char_new_line()
		else:
			self.pos = self.pos.advance_same_line(1)

	def advance_same_line(self, count):
		self.pos = self.pos.advance_same_line(count)

	def analyze_raw_1(self, word):
		if self.buf.startswith(word, self.pos.char):
			self.advance_same_line(len(word))
			return True
		else:
			return False

	def analyze_raw_synonyms(self, synonyms):
		for word in synonyms:
			if self.analyze_raw_1(word):
				return True
		return False

	def skip_white(self):
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

	def analyze_keyword(self, synonyms):
		self.skip_white()
		for word in synonyms:
			before_word = self.pos
			if self.analyze_raw_1(word):
				if is_ident_char_2(self.cc()):
					# rewind
					self.pos = before_word
				else:
					self.advance1()
					return True
		return False

	def analyze_instruction(self):
# TODO ! à implémenter !
		print ("TODO!!!")
		return False
