import re
import keywords as kw
import errors
from position import Position

re_identifier = re.compile(r'^[^\d\W]\w*', re.UNICODE)

class Parser:
	'''
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and True is returned.
	Otherwise, the current position is left untouched, and False is returned.
	These functions may raise an exception if a syntax error was found.
	'''

	def __init__(self, path):
		self.pos = Position(path)
		with open(path, 'r') as input_file:
			self.buf = input_file.read()

	@property
	def cc(self):
		'''
		Return the current character in the buffer.
		'''
		return self.buf[self.pos.char]
	
	@property
	def sliced_buf(self):
		'''
		Return a sliced view of the buffer that starts at the current position.
		'''
		return self.buf[self.pos.char:]

	def advance1(self):
		'''
		Advance current position in the buffer by one character and update self.pos
		accordingly.
		'''
		if self.cc == '\n':
			self.pos = self.pos.next_char_new_line()
		else:
			self.pos = self.pos.advance_same_line(1)

	def advance_same_line(self, n):
		'''
		Advance current position in the buffer by n characters and update self.pos
		accordingly.
		'''
		self.pos = self.pos.advance_same_line(n)

	def skip_white(self):
		'''
		Skip any whitespace and comments starting at the current position and
		updates self.pos accordingly.
		'''
		state = 'WHITE'
		while state != 'END':
			if state is 'WHITE':
				# plain whitespace
				if self.cc.isspace():
					self.advance1()
				elif self.analyze_keyword(kw.MLC_START, False):
					state = 'MULTI'
				elif self.analyze_keyword(kw.SLC_START, False):
					state = 'SINGLE'
				else:
					state = 'END'
			elif state is 'MULTI':
				# inside multi-line comment
				if self.analyze_keyword(kw.MLC_END, False):
					state = 'WHITE'
				else:
					self.advance1()
			elif state is 'SINGLE':
				# inside single-line comment
				if self.cc == '\n':
					state = 'WHITE'
				self.advance1()

	def analyze_algorithm(self):
		if not self.analyze_keyword(kw.ALGORITHM):
			return False
		self.analyze_mandatory_keyword(kw.BEGIN)
		while self.analyze_instruction():
# TODO !!! faire pour de vrai analyze_instruction()
			pass
		self.analyze_mandatory_keyword(kw.END)
		return True

	def analyze_function(self):
		if not self.analyze_keyword(kw.FUNCTION):
			return False

		name = self.analyze_identifier()
		if not name:
			raise errors.IllegalIdentifier(self.pos)

		self.analyze_mandatory_keyword(kw.LPAREN)

		params = []

		if not self.analyze_keyword(kw.RPAREN):
			# non-empty parameter list
			self.analyze_formal_parameter()
			while self.analyze_keyword(kw.COMMA):
				p = self.analyze_formal_parameter()
				params.append(p)
			self.analyze_mandatory_keyword(kw.RPAREN)

		if self.analyze_keyword(kw.COLON):
			raise errors.UnimplementedError(self.pos, \
					"type de retour de la fonction")

		self.analyze_mandatory_keyword(kw.BEGIN)
		while self.analyze_instruction():
# TODO
			pass

		self.analyze_mandatory_keyword(kw.END)

	def analyze_formal_parameter(self):
		name = self.analyze_identifier()
		if not name:
			raise errors.IllegalIdentifier(self.pos)

		is_inout = self.analyze_keyword(kw.INOUT)

		self.analyze_mandatory_keyword(kw.COLON)

		is_array = self.analyze_keyword(kw.ARRAY)

		type_kw = None
		for candidate in kw.meta.all_types:
			if self.analyze_keyword(candidate):
				type_kw = candidate
				break
		if not type_kw:
			raise errors.ExpectedItemError(self.pos, "un type")

		if is_array:
			self.analyze_mandatory_keyword(kw.LSBRACKET)
			raise errors.UnimplementedError(self.pos, \
					"taille du tableau paramètre effectif")

		raise errors.UnimplementedError(self.pos, \
				"création adéquate objet param formel")

		#return FormalParameter(name, type_kw)

	def analyze_identifier(self):
		self.skip_white()
		match = re_identifier.match(self.sliced_buf)
		if not match:
			return False
		identifier = match.group(0)
		self.advance_same_line(len(identifier))
		return identifier

	def analyze_keyword(self, keyword, skip_white=True):
		if skip_white:
			self.skip_white()
		found = keyword.find(self.sliced_buf)
		if not found:
			return False
		self.advance_same_line(len(found))
		return found

	def analyze_mandatory_keyword(self, keyword):
		found = self.analyze_keyword(keyword)
		if not found:
			raise errors.ExpectedKeywordError(self.pos, keyword)
		return found

	def analyze_instruction(self):
		'''
		Analyze an instruction.
		'''
# TODO ! à implémenter !
		print ("TODO!!!")
		return False
