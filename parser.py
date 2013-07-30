import re
import keywords as kw
import errors
from position import Position
from tree import *

re_identifier = re.compile(r'^[^\d\W]\w*', re.UNICODE)
re_integer    = re.compile(r'^[+\-]?\d+[^\.\w]', re.UNICODE)
re_real       = re.compile(r'^[+\-]?\d+\.?\d*[^\w]', re.UNICODE)
re_string     = re.compile(r'^".*?"', re.UNICODE) # TODO- escaping

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
		with open(path, 'r', encoding='utf-8') as input_file:
			self.buf = input_file.read()
			self.buflen = len(self.buf)

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

	def advance(self, chars=0, skip_white=True):
		'''
		Advance current position in the buffer so that the cursor points on something 
		significant (i.e. no whitespace, no comments)

		This function must be called at the very beginning of a source file, and 
		after every operation that permanently consumes bytes from the buffer.
		'''
		if chars != 0:
			self.pos = self.pos.advance_same_line(chars)
		if not skip_white:
			return
		state = 'WHITE'
		while state != 'END' and not self.eof():
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

	def eof(self):
		return self.pos.char >= self.buflen

	def analyze_top_level(self):
		def analyze_top_level_node():
			for analyze in [self.analyze_function, self.analyze_algorithm]:
				thing = analyze()
				if thing:
					return thing
			return False
		self.advance()
		top_level_nodes = []
		while not self.eof():
			thing = analyze_top_level_node()
			if thing:
				top_level_nodes.append(thing)
			else:
				raise errors.ExpectedItemError(self.pos, "une fonction ou un algorithme")
		return top_level_nodes

	def analyze_algorithm(self):
		start_kw = self.analyze_keyword(kw.ALGORITHM)
		if not start_kw:
			return False
		# point of no-return
		self.analyze_mandatory_keyword(kw.BEGIN)
		body,_ = self.analyze_instruction_block(kw.END)
		return Algorithm(start_kw.pos, body)

	def analyze_function(self):
		start_kw = self.analyze_keyword(kw.FUNCTION)
		if not start_kw:
			return False

		# point of no-return
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

		body,_ = self.analyze_instruction_block(kw.END)
		return Function(start_kw.pos, name, params, body)

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

		return FormalParameter(name.pos, name, type_kw)

	def analyze_identifier(self):
		match = re_identifier.match(self.sliced_buf)
		if not match:
			return False
		identifier = match.group(0)
		# invalid identifier if the string is a keyword
		if identifier in kw.meta.all_keywords:
			return False
		pos0 = self.pos
		self.advance(len(identifier))
		return Identifier(pos0, identifier)

	def analyze_keyword(self, keyword, skip_white=True):
		pos0 = self.pos
		found = keyword.find(self.sliced_buf)
		if not found:
			return False
		self.advance(len(found), skip_white)
		return Keyword(pos0, found)

	def analyze_mandatory_keyword(self, keyword):
		found = self.analyze_keyword(keyword)
		if not found:
			raise errors.ExpectedKeywordError(self.pos, keyword)
		return found
	
	def analyze_optional_keyword(self, keyword):
		return self.analyze_keyword(keyword)

	def analyze_instruction_block(self, *end_marker_keywords):
		block = []
		while True:
			instruction = self.analyze_instruction()
			if instruction:
				block.append(instruction)
			else:
				break
		for emk in end_marker_keywords:
			if self.analyze_keyword(emk) is not None:
				return block, emk

	def analyze_instruction(self):
		analyse_order = [
			self.analyze_assignment,
			self.analyze_function_call,
			self.analyze_instruction_if,
			self.analyze_instruction_for,
			self.analyze_instruction_while,
			self.analyze_instruction_dowhile
			]
			
		for analyze in analyse_order:
			instruction = analyze()
			if instruction:
				return instruction
		return False

	def analyze_assignment(self):
		pos0 = self.pos

		identifier = self.analyze_identifier()
		if not identifier: 
			return False

		if not self.analyze_keyword(kw.ASSIGN):
			self.pos = pos0
			return False

		# point of no return
		rhs = self.analyze_expression()
		if not rhs:
			raise errors.ExpectedItemError(self.pos, "une expression")

		return Assignment(pos0, identifier, rhs)

	def analyze_function_call(self):
		pos0 = self.pos

		function_name = self.analyze_identifier()
		if not function_name:
			return False

		if not self.analyze_keyword(kw.LPAREN):
			self.pos = pos0
			return False

		# point of no return
		effective_parameters = []
		if not self.analyze_keyword(kw.RPAREN):
			next_parameter = True
			while next_parameter:
				parameter = self.analyze_expression()
				if not parameter:
					raise errors.ExpectedItemError(self.pos,\
							"une expression comme paramètre effectif")
				effective_parameters.append(parameter)
				next_parameter = self.analyze_keyword(kw.COMMA)
			self.analyze_mandatory_keyword(kw.RPAREN)

		return FunctionCall(pos0, function_name, effective_parameters)
	
	def analyze_instruction_if(self):
		pos0 = self.pos

		if not self.analyze_keyword(kw.IF):
			self.pos = pos0
			return False

		# point of no return
		bool_Expr = self.analyze_expression()
		if not bool_Expr:
			raise errors.ExpectedItemError(self.pos, "une expression")

		self.analyze_mandatory_keyword(kw.THEN)
		
		first_block,emk = self.analyze_instruction_block(kw.ELSE, kw.END_IF)
		optional_block = None
		
		if emk == kw.ELSE :
			optional_block,_ = self.analyze_instruction_block(kw.END_IF)
			
		return InstructionIf(pos0, bool_Expr, first_block, optional_block )
		
	def analyze_instruction_for(self):
		pos0 = self.pos

		if not self.analyze_keyword(kw.FOR):
			self.pos = pos0
			return False

		# point of no return
		increment = self.analyze_identifier()
		if not increment:
			raise errors.ExpectedItemError(self.pos, "un identifieur")
		
		self.analyze_mandatory_keyword(kw.FROM)
		int_from = self.analyze_expression()
		if not int_from:
			raise errors.ExpectedItemError(self.pos, "un identifieur")

		self.analyze_mandatory_keyword(kw.TO)
		int_to = self.analyze_expression()
		if not int_to:
			raise errors.ExpectedItemError(self.pos, "un identifieur")
		
		self.analyze_mandatory_keyword(kw.DO)
		
		block,_ = self.analyze_instruction_block(kw.END_FOR)
		
		return InstructionFor(pos0, increment, int_from, int_to, block )
	
	def analyze_instruction_while(self):
		pos0 = self.pos

		if not self.analyze_keyword(kw.WHILE):
			self.pos = pos0
			return False

		# point of no return
		bool_Expr = self.analyze_expression()
		if not bool_Expr:
			raise errors.ExpectedItemError(self.pos, "une expression")

		self.analyze_mandatory_keyword(kw.DO)
		
		block,_ = self.analyze_instruction_block(kw.END_WHILE)
		
		return InstructionWhile(pos0, bool_Expr, block )
		
	def analyze_instruction_dowhile(self):
		pos0 = self.pos

		if not self.analyze_keyword(kw.DO):
			self.pos = pos0
			return False

		# point of no return
		block,_ = self.analyze_instruction_block(kw.TO)
		bool_Expr = self.analyze_expression()
		if not bool_Expr:
			raise errors.ExpectedItemError(self.pos, "une expression")
		return InstructionDoWhile(pos0, block, bool_Expr)
		
	def analyze_expression(self):
		analysis_order = [
				self.analyze_literal_integer,
				self.analyze_literal_real,
				self.analyze_literal_string,
		]
		for analyze in analysis_order:
			expression = analyze()
			if expression:
				return expression
		return False

	def analyze_literal_integer(self):
		pos0 = self.pos
		match = re_integer.match(self.sliced_buf)
		if not match:
			return False
		integer_string = match.group(0)
		self.advance(len(integer_string))
		return LiteralInteger(pos0, int(integer_string))

	def analyze_literal_real(self):
		pos0 = self.pos
		match = re_real.match(self.sliced_buf)
		if not match:
			return False
		real_string = match.group(0)
		self.advance(len(real_string))
		return LiteralReal(pos0, float(real_string))

	def analyze_literal_string(self):
		pos0 = self.pos
		match = re_string.match(self.sliced_buf)
		if not match:
			return False
		string_string = match.group(0)
		self.advance(len(string_string))
		# return string_string without the surrounding quotes
		# TODO- when we allow escaping it'll be more complex than just removing the quotes
		return LiteralString(pos0, string_string[1:-1])
