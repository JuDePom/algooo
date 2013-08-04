import re
import ldakeywords as kw
import operators as ops
from errors import *
from position import Position
from tree import *

re_identifier = re.compile(r'^[^\d\W]\w*', re.UNICODE)

# match at least one digit;
# must NOT followed by a dot, an alpha, or a _
re_integer    = re.compile(r'^\d+(?![\w\.])', re.UNICODE)

# match at least one digit, one dot, and zero or more digits, 
# **OR** match one dot, and at least one digit;
# but either match must NOT be followed by another dot, an alpha, or a _
re_real       = re.compile(r'^(\d+\.\d*|\.\d+)(?![\w\.])', re.UNICODE)

re_string     = re.compile(r'^".*?"', re.UNICODE) # TODO- escaping

class Parser:
	'''
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and True is returned.
	Otherwise, the current position is left untouched, and None is returned.
	These functions may raise an exception if a syntax error was found.
	'''

	def __init__(self, path):
		self.pos = Position(path)
		with open(path, 'rt', encoding='utf8') as input_file:
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
		self.advance()
		top_level_nodes = []
		while not self.eof():
			top = self.analyze_multiple(self.analyze_function, self.analyze_algorithm)
			if top is None:
				raise ExpectedItemError(self.pos, "une fonction ou un algorithme")
			top_level_nodes.append(top)
		return top_level_nodes
		
	def analyze_algorithm(self):
		start_kw = self.analyze_keyword(kw.ALGORITHM)
		if start_kw is None:
			return

		# point of no-return
		lexi = self.analyze_lexicon()
		if lexi is None:
			raise ExpectedItemError(self.pos, "le lexique de la fonction")
		self.analyze_mandatory_keyword(kw.BEGIN)
		body,_ = self.analyze_instruction_block(kw.END)
		return Algorithm(start_kw.pos, lexi, body)

	def analyze_function(self):
		start_kw = self.analyze_keyword(kw.FUNCTION)
		if start_kw is None:
			return

		# point of no-return
		name = self.analyze_identifier()
		if name is None:
			raise IllegalIdentifier(self.pos)

		self.analyze_mandatory_keyword(kw.LPAREN)

		if self.analyze_keyword(kw.RPAREN) is None:
			# non-empty parameter list
			params = self.analyze_comma_separated_args(self.analyze_formal_parameter)
			self.analyze_mandatory_keyword(kw.RPAREN)
		else:
			# got an RPAREN right away: empty parameter list
			params = []

		if self.analyze_keyword(kw.COLON) is not None:
			raise UnimplementedError(self.pos, \
					"type de retour de la fonction")

		lexi = self.analyze_lexicon()
		# TODO - on laisse les lexiques vides jusqu'à l'analyse sémantique ?
		#if lexi is None:
			#raise ExpectedItemError(self.pos, "le lexique de la fonction")

		self.analyze_mandatory_keyword(kw.BEGIN)
		body, _ = self.analyze_instruction_block(kw.END)

		return Function(start_kw.pos, name, params, lexi, body)

	def analyze_formal_parameter(self):
		pos0 = self.pos

		name = self.analyze_identifier()
		if name is None:
			return

		is_inout = self.analyze_keyword(kw.INOUT) is not None

		if self.analyze_keyword(kw.COLON) is None:
			self.pos = pos0
			return

		is_array = self.analyze_keyword(kw.ARRAY) is not None

		type_ = None
		for candidate in kw.meta.all_scalar_types:
			if self.analyze_keyword(candidate) is not None:
				type_ = candidate
				break
		if type_ is None:
			type_ = self.analyze_identifier()
		if type_ is None:
			raise ExpectedItemError(self.pos, \
					"un type scalaire ou composite")

		if is_array:
			self.analyze_mandatory_keyword(kw.LSBRACK)
			array_dimensions = self.analyze_comma_separated_args(self.analyze_expression)
			self.analyze_mandatory_keyword(kw.RSBRACK)
		else:
			array_dimensions = None

		return FormalParameter(name, type_, is_inout, array_dimensions)

	def analyze_lexicon(self):
		start_kw = self.analyze_keyword(kw.LEXICON)
		if start_kw is None:
			return
		declarations = []
		molds = []
		while True:
			d = self.analyze_formal_parameter()
			if d is not None:
				declarations.append(d)
				continue
			m = self.analyze_compound_mold_declaration()
			if m is not None:
				molds.append(m)
				continue
			break
		return Lexicon(start_kw.pos, declarations, molds)	

	def analyze_identifier(self):
		match = re_identifier.match(self.sliced_buf)
		if match is None:
			return
		identifier = match.group(0)
		if identifier in kw.meta.all_keywords:
			return # invalid identifier if the string is a keyword
		pos0 = self.pos
		self.advance(len(identifier))
		return Identifier(pos0, identifier)

	def analyze_keyword(self, keyword, skip_white=True):
		pos0 = self.pos
		found_string = keyword.find(self.sliced_buf)
		if found_string is not None:
			self.advance(len(found_string), skip_white)
			return KeywordToken(pos0, found_string)

	def analyze_mandatory_keyword(self, keyword):
		found_kw = self.analyze_keyword(keyword)
		if found_kw is not None:
			return found_kw
		else:
			raise ExpectedKeywordError(self.pos, keyword)

	def analyze_compound_mold_declaration(self):
		pos0 = self.pos
		
		name_id = self.analyze_identifier()
		if name_id is None:
			return

		if self.analyze_keyword(kw.EQ) is None:
			self.pos = pos0
			return

		# point of no return
		self.analyze_mandatory_keyword(kw.LT)
		fp_list = self.analyze_comma_separated_args(self.analyze_formal_parameter)
		self.analyze_mandatory_keyword(kw.GT)
		return CompoundMold(name_id, fp_list)

	def analyze_instruction_block(self, *end_marker_keywords):
		pos0 = self.pos
		statements = []
		instruction = self.analyze_instruction()
		while instruction is not None:
			statements.append(instruction)
			instruction = self.analyze_instruction()
		for marker in end_marker_keywords:
			if self.analyze_keyword(marker) is not None:
				return StatementBlock(pos0, statements), marker
		raise ExpectedKeywordError(self.pos, *end_marker_keywords)
	
	def analyze_multiple(self, *analysis_order):
		for thing in (analyze() for analyze in analysis_order):
			if thing is not None:
				return thing

	def analyze_instruction(self):
		return self.analyze_multiple(
			self.analyze_expression,
			self.analyze_if,
			self.analyze_for,
			self.analyze_while,
			self.analyze_do_while)

	def analyze_if(self):
		pos0 = self.pos

		if self.analyze_keyword(kw.IF) is None: return

		# point of no return
		condition = self.analyze_expression()
		if condition is None:
			raise ExpectedItemError(self.pos,
					"l'expression de la condition")

		self.analyze_mandatory_keyword(kw.THEN)
		
		first_block, emk = self.analyze_instruction_block(kw.ELSE, kw.END_IF)
		
		if emk == kw.ELSE:
			optional_block,_ = self.analyze_instruction_block(kw.END_IF)
		else:
			optional_block = None

		return InstructionIf(pos0, condition, first_block, optional_block)
		
	def analyze_for(self):
		pos0 = self.pos

		if self.analyze_keyword(kw.FOR) is None: return

		# point of no return
		increment = self.analyze_identifier()
		if increment is None:
			raise ExpectedItemError(self.pos, 
					"l'identifieur du compteur de la boucle")
		
		self.analyze_mandatory_keyword(kw.FROM)
		int_from = self.analyze_expression()
		if int_from is None:
			raise ExpectedItemError(self.pos,
					"l'expression de la valeur de départ du compteur")

		self.analyze_mandatory_keyword(kw.TO)
		int_to = self.analyze_expression()
		if int_to is None:
			raise ExpectedItemError(self.pos,
					"l'expression de la valeur finale du compteur")
		
		self.analyze_mandatory_keyword(kw.DO)
		
		block,_ = self.analyze_instruction_block(kw.END_FOR)
		
		return InstructionFor(pos0, increment, int_from, int_to, block)
	
	def analyze_while(self):
		pos0 = self.pos

		if self.analyze_keyword(kw.WHILE) is None: return

		# point of no return
		bool_Expr = self.analyze_expression()
		if bool_Expr is None:
			raise ExpectedItemError(self.pos,
					"l'expression de la condition de la boucle")

		self.analyze_mandatory_keyword(kw.DO)
		
		block,_ = self.analyze_instruction_block(kw.END_WHILE)
		
		return InstructionWhile(pos0, bool_Expr, block)
		
	def analyze_do_while(self):
		pos0 = self.pos

		if self.analyze_keyword(kw.DO) is None: return 

		# point of no return
		block,_ = self.analyze_instruction_block(kw.TO)
		bool_Expr = self.analyze_expression()
		if bool_Expr is None:
			raise ExpectedItemError(self.pos,
					"l'expression de la condition de la boucle")
		return InstructionDoWhile(pos0, block, bool_Expr)
	
	def analyze_expression(self):
		lhs = self.analyze_primary_expression()
		t   = self.analyze_binary_operator()
		expr, _ = self.analyze_partial_expression(lhs, t)
		return expr
	
	def analyze_partial_expression(self, lhs, t, min_p=0):
		assert(t is None or (type(t) is OperatorToken and t.op.binary))
		while t is not None and t.op.precedence >= min_p:
			op_tok = t
			op = t.op
			rhs = self.analyze_second_operand(op)
			t = self.analyze_binary_operator()
			while t is not None and \
					(t.op.precedence > op.precedence or \
					(t.op.right_ass and t.op.precedence == op.precedence)):
				rhs, t = self.analyze_partial_expression(rhs, t, t.op.precedence)
			lhs = BinaryOpNode(op_tok, lhs, rhs)
		return lhs, t

	def analyze_second_operand(self, op):
		pos0 = self.pos
		if op.encompass_till is None:
			return self.analyze_primary_expression(op.precedence)
		elif op.encompass_several:
			arg_list = self.analyze_comma_separated_args(self.analyze_expression)
			rhs = Varargs(pos0, arg_list)
		else:
			rhs = self.analyze_expression()
		self.analyze_mandatory_keyword(op.encompass_till)
		return rhs

	def analyze_comma_separated_args(self, analyze_arg):
		arg_list = []
		next_arg = True
		while next_arg:
			arg = analyze_arg()
			if arg is not None:
				arg_list.append(arg)
			next_arg = self.analyze_keyword(kw.COMMA) is not None
			if next_arg and arg is None:
				raise LDASyntaxError(self.pos, "argument vide")
		return arg_list

	def analyze_primary_expression(self, min_unary_precedence=0):
		lparen = self.analyze_keyword(kw.LPAREN)
		if lparen is not None:
			sub_expr = self.analyze_expression()
			self.analyze_mandatory_keyword(kw.RPAREN)
			return sub_expr
		
		unary = self.analyze_unary_operator()
		if unary is not None:
			if unary.op.precedence < min_unary_precedence:
				raise LDASyntaxError("précédence trop faible") # TODO - mieux expliquer
			# analyze primary after the unary operator
			primary = self.analyze_primary_expression(unary.op.precedence)
			return UnaryOpNode(unary, primary)

		return self.analyze_expression_non_op_token()

	def analyze_operator(self, operator_list):
		for op in operator_list:
			op_kw = self.analyze_keyword(op.symbol)
			if op_kw is not None:
				return OperatorToken(op_kw, op)
	
	def analyze_binary_operator(self):
		return self.analyze_operator(ops.meta.all_binaries)

	def analyze_unary_operator(self):
		return self.analyze_operator(ops.meta.all_unaries)

	def analyze_expression_non_op_token(self):
		return self.analyze_multiple(
				self.analyze_literal_integer,
				self.analyze_literal_real,
				self.analyze_literal_string,
				self.analyze_literal_boolean,
				self.analyze_identifier,)

	def analyze_literal_integer(self):
		pos0 = self.pos
		match = re_integer.match(self.sliced_buf)
		if match is not None:
			integer_string = match.group(0)
			self.advance(len(integer_string))
			return LiteralInteger(pos0, int(integer_string))

	def analyze_literal_real(self):
		pos0 = self.pos
		match = re_real.match(self.sliced_buf)
		if match is not None:
			real_string = match.group(0)
			self.advance(len(real_string))
			return LiteralReal(pos0, float(real_string))

	def analyze_literal_string(self):
		pos0 = self.pos
		match = re_string.match(self.sliced_buf)
		if match is not None:
			string_string = match.group(0)
			self.advance(len(string_string))
			# return string_string without the surrounding quotes
			# TODO- when we allow escaping it'll be more complex than just removing the quotes
			return LiteralString(pos0, string_string[1:-1])

	def analyze_literal_boolean(self):
		pos0 = self.pos
		true_kw = self.analyze_keyword(kw.TRUE)
		if true_kw is None and self.analyze_keyword(kw.FALSE) is None:
			return
		value = true_kw is not None
		return LiteralBoolean(pos0, value)

