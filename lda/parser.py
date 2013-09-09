import re
from . import kw
from . import module
from . import position
from . import expression
from . import operators
from . import statements
from . import symbols
from . import types
from .errors import syntax

re_identifier = re.compile(r'''
	[^\d\W]    # The first character must be a non-digital word character.
	\w*        # After that, all word characters are allowed.
	''', re.VERBOSE)

re_integer = re.compile(r'''
	\d+(       # At least one digit.
	(?![\.\w]) # The last digit may not be followed by a single dot (that would
	           # make it a real number) or a word character.
	|(?=\.\.)  # But the last digit may be followed by two dots (range operator).
	)''', re.VERBOSE)

re_real = re.compile(r'''
	(\d+\.\d*  # At least one digit, followed by a dot, and zero or more digits.
	|\.\d+)    # Or a dot followed by at least one digit.
	((?![\.\w])# The last digit may not be followed by another dot
	           # or a "word" character.
	|(?=\.\.)  # But the last digit may be followed by two dots (range operator).
	           # (Although semantically, ranges can't contain reals.)
	)''', re.VERBOSE)

re_string = re.compile(r'".*?"') # TODO- escaping

re_character = re.compile(r"'.'") # TODO- escaping

class RelevantFailureLogger:
	"""
	Parser context manager that keeps track of the most relevant syntax error.

	The most relevant syntax error is that which was raised at the furthest
	point in the input source code.

	By default, this context manager lets the syntax error propagate through
	the method syntax_error(), but this behavior can be overridden.
	"""

	def __init__(self, parser):
		self.parser = parser

	def __enter__(self):
		self.pos = self.parser.pos

	def __exit__(self, exc_type, exc_value, traceback):
		if isinstance(exc_value, syntax.SyntaxError):
			self.parser.append_syntax_error(exc_value)
			return self.syntax_error(exc_value)
		else:
			# Unknown error. Let Python handle it.
			return False

	def syntax_error(self, exc_value):
		# Propagate exception
		return False

class BacktrackFailure(RelevantFailureLogger):
	"""
	Parser context manager that backtracks on syntax errors. It also keeps
	track of the most relevant syntax error (see RelevantFailureLogger).

	If a syntax error is found, the parser's position is reverted to the
	position at which the context was entered.

	Note: This context manager does NOT let syntax errors propagate!
	"""

	def syntax_error(self, exc_value):
		self.parser.pos = self.pos
		# Don't let the exception propagate
		return True

class CriticalItem(RelevantFailureLogger):
	"""
	Parser context manager that raises an ExpectedItem exception on syntax
	errors. It also keeps track of the most relevant syntax error, but NOT of
	the ExpectedItem exception it raises itself.
	"""

	def __init__(self, parser, expected_item_name=None):
		super().__init__(parser)
		self.expected_item_name = expected_item_name

	def syntax_error(self, exc_value):
		raise syntax.ExpectedItem(self.pos, self.expected_item_name)

class Parser:
	"""
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and the item is returned.
	Otherwise, a SyntaxError exception is raised and the current position is
	left where the parser managed to make inroads.

	Not all SyntaxError exceptions are necessarily fatal; hence the use of the
	BacktrackFailure context manager to fail gracefully.
	"""

	def __init__(self, options, path=None):
		self.options = options
		if path is not None:
			self.path = path
			with open(path, 'rt', encoding='utf8') as input_file:
				self.set_buf(input_file.read())

	def reset_pos(self):
		self.pos = position.Position(self.path)

	def set_buf(self, value):
		self.path = "<direct>"
		self.syntax_errors = []
		# raw_buf: only used to parse strings and characters
		self.raw_buf = value
		# buf: for everything else.
		# This allows the parser to ignore the case if needed.
		if self.options.case_insensitive:
			self.buf = value.lower()
		else:
			self.buf = value
		self.buflen = len(self.buf)
		self.reset_pos()
		# skip initial whitespace
		self.advance()

	def append_syntax_error(self, new_error):
		if not self.syntax_errors or new_error.pos > self.relevant_syntax_error.pos:
			self.syntax_errors = [new_error]
		elif new_error.pos == self.relevant_syntax_error.pos:
			self.syntax_errors.append(new_error)

	@property
	def relevant_syntax_error(self):
		return self.syntax_errors[-1]

	def advance(self, chars=0):
		"""
		Advance current position in the buffer so that the cursor points on something
		significant (i.e. no whitespace, no comments)

		This function must be called at the very beginning of a source file, and
		after every operation that permanently consumes bytes from the buffer.
		"""
		bpos = self.pos.char
		line = self.pos.line
		column = self.pos.column
		if chars != 0:
			bpos += chars
			column += chars
		in_multi = False
		while bpos != -1 and bpos < self.buflen:
			if self.buf[bpos] == '\n':
				bpos += 1
				line += 1
				column = 1
			elif not in_multi:
				if self.buf[bpos].isspace():
					bpos += 1
					column += 1
				elif self.buf.startswith('(*', bpos):
					bpos += 2
					in_multi = True
				elif self.buf.startswith('//', bpos):
					bpos = self.buf.find('\n', bpos+2)
				else:
					break
			else:
				if self.buf.startswith('*)', bpos):
					bpos += 2
					in_multi = False
				else:
					bpos += 1
					column += 1
		self.pos = position.Position(self.pos.path, bpos, line, column)

	def eof(self):
		return self.pos.char >= self.buflen

	def traverse_synonym_priority_chain(self, syn):
		"""
		Return keyword synonym with highest priority over syn at the current
		position in the buffer, or return syn if syn must not give way to any
		synonym at the current position.
		"""
		for gw in syn.give_way:
			found = self.traverse_synonym_priority_chain(gw)
			if found is not None:
				return found
		if self.buf.startswith(syn.word, self.pos.char):
			return syn

	def consume_keyword(self, keyword, soft=False):
		cached_alpha = None
		for syn in keyword.synonyms:
			if syn.gluable:
				found = self.traverse_synonym_priority_chain(syn)
				if found is None:
					continue
				elif found == syn:
					# found this synonym
					self.advance(len(syn.word))
					return True
				else:
					# gave way to another keyword
					break
			else:
				if cached_alpha is None:
					try:
						cached_alpha = self.consume_regex(re_identifier, advance=False)
					except syntax.ExpectedItem:
						continue
				if cached_alpha == syn.word:
					self.advance(len(syn.word))
					return True
		if soft:
			return False
		else:
			raise syntax.ExpectedKeyword(self.pos, keyword)

	def consume_keyword_choice(self, *choices):
		for keyword in choices:
			if self.consume_keyword(keyword, soft=True):
				return keyword
		raise syntax.ExpectedKeyword(self.pos, *choices)

	def analyze_multiple(self, group_name, *analysis_order):
		for analyze in analysis_order:
			with BacktrackFailure(self):
				return analyze()
		raise syntax.ExpectedItem(self.pos, group_name)

	def analyze_module(self):
		functions = []
		algorithms = []
		lexicon = None
		with BacktrackFailure(self):
			lexicon = self.analyze_lexicon()
		while not self.eof():
			with BacktrackFailure(self):
				functions.append(self.analyze_function())
				continue
			with BacktrackFailure(self):
				algorithms.append(self.analyze_algorithm())
				continue
			with RelevantFailureLogger(self):
				raise syntax.ExpectedItem(self.pos, "une fonction ou un algorithme")
		return module.Module(lexicon, functions, algorithms)

	def analyze_algorithm(self):
		pos = self.pos
		self.consume_keyword(kw.ALGORITHM)
		# lexicon
		lexicon = None
		with BacktrackFailure(self):
			lexicon = self.analyze_lexicon()
		# statement block
		self.consume_keyword(kw.BEGIN)
		body, _, _ = self.analyze_statement_block(kw.END)
		return module.Algorithm(pos, lexicon, body)

	def analyze_function(self):
		pos = self.pos
		self.consume_keyword(kw.FUNCTION)
		# identifier
		ident = self.analyze_identifier()
		# left parenthesis
		self.consume_keyword(kw.LPAREN)
		# formal parameters, or lack thereof
		if self.consume_keyword(kw.RPAREN, soft=True):
			# got an RPAREN right away: empty parameter list
			params = []
		else:
			# non-empty parameter list
			params = self.analyze_arglist(self.analyze_field, formal=True)
			self.consume_keyword(kw.RPAREN)
		# optional colon before return type (if omitted, no return type)
		if self.consume_keyword(kw.COLON, soft=True):
			with CriticalItem(self, "type de retour de la fonction"):
				return_type = self.analyze_type_descriptor()
		else:
			return_type = types.VOID
		# lexicon
		lexicon = None
		with BacktrackFailure(self):
			lexicon = self.analyze_lexicon()
		# statement block
		self.consume_keyword(kw.BEGIN)
		body, _, _ = self.analyze_statement_block(kw.END)
		return module.Function(pos, ident, params, return_type, lexicon, body)

	def analyze_scalar_type(self):
		scalar_dict = {
				kw.INT    : types.INTEGER,
				kw.REAL   : types.REAL,
				kw.BOOL   : types.BOOLEAN,
				kw.CHAR   : types.CHARACTER,
				kw.STRING : types.STRING,
		}
		scalar_kw = self.consume_keyword_choice(*scalar_dict.keys())
		return scalar_dict[scalar_kw]

	def analyze_array(self):
		self.consume_keyword(kw.ARRAY)
		element_type = self.analyze_non_array_type_descriptor()
		lsbrack_pos = self.pos
		self.consume_keyword(kw.LSBRACK)
		dimensions = self.analyze_arglist(self.analyze_array_dimension)
		self.consume_keyword(kw.RSBRACK)
		return types.Array(lsbrack_pos, element_type, dimensions)

	def analyze_array_dimension(self):
		return self.analyze_multiple("une dimension de tableau statique ou dynamique",
				self.analyze_static_array_dimension,
				self.analyze_dynamic_array_dimension)

	def analyze_static_array_dimension(self):
		return types.Array.StaticDimension(self.analyze_expression())

	def analyze_dynamic_array_dimension(self):
		pos = self.pos
		self.consume_keyword(kw.QUESTION_MARK)
		return types.Array.DynamicDimension(pos)

	def analyze_type_alias(self):
		return self.analyze_identifier(symbols.TypeAlias)

	def analyze_type_descriptor(self):
		inout = self.consume_keyword(kw.INOUT, soft=True)
		type_descriptor = None
		with BacktrackFailure(self):
			type_descriptor = self.analyze_array()
		if type_descriptor is None:
			type_descriptor = self.analyze_non_array_type_descriptor()
		if not inout:
			return type_descriptor
		else:
			return types.Inout(type_descriptor)

	def analyze_non_array_type_descriptor(self):
		return self.analyze_multiple("un descripteur de type non-tableau",
			self.analyze_scalar_type,
			self.analyze_type_alias)

	def analyze_field(self, formal=False):
		ident = self.analyze_identifier()
		self.consume_keyword(kw.COLON)
		type_descriptor = self.analyze_type_descriptor()
		return symbols.Field(ident, type_descriptor, formal)

	def analyze_composite(self):
		ident = self.analyze_identifier()
		self.consume_keyword(kw.EQ)
		self.consume_keyword(kw.LT)
		field_list = self.analyze_arglist(self.analyze_field)
		self.consume_keyword(kw.GT)
		return types.Composite(ident, field_list)

	def analyze_lexicon(self):
		self.consume_keyword(kw.LEXICON)
		variables = []
		composites = []
		while True:
			with BacktrackFailure(self):
				variables.append(self.analyze_field())
				continue
			with BacktrackFailure(self):
				composites.append(self.analyze_composite())
				continue
			break
		return symbols.Lexicon(variables, composites)

	def analyze_identifier(self, identifier_class=symbols.Identifier):
		pos = self.pos
		try:
			name = self.consume_regex(re_identifier, advance=False)
		except syntax.ExpectedItem:
			raise syntax.IllegalIdentifier(self.pos)
		if name in kw.reserved:
			raise syntax.ReservedWord(self.pos, name)
		self.advance(len(name))
		return identifier_class(pos, name)

	def analyze_statement_block(self, *end_marker_keywords):
		"""
		Build a statement block until an end marker keyword is found.
		Return a tuple containing:
		- the statement block
		- the encountered end marker
		- the end marker's position
		"""
		pos = self.pos
		block = []
		while True:
			with BacktrackFailure(self):
				unit = self.analyze_statement()
				block.append(unit)
				continue
			break
		marker_pos = self.pos
		marker = self.consume_keyword_choice(*end_marker_keywords)
		return statements.StatementBlock(pos, block), marker, marker_pos

	def analyze_statement(self):
		return self.analyze_multiple("une instruction",
				self.analyze_assignment,
				self.analyze_return,
				self.analyze_expression,
				self.analyze_if,
				self.analyze_for,
				self.analyze_while,)

	def analyze_assignment(self):
		lhs = self.analyze_expression()
		kw_pos = self.pos
		self.consume_keyword(kw.ASSIGN)
		rhs = self.analyze_expression()
		return statements.Assignment(kw_pos, lhs, rhs)

	def analyze_return(self):
		pos = self.pos
		self.consume_keyword(kw.RETURN)
		expr = None
		with BacktrackFailure(self):
			expr = self.analyze_expression()
		return statements.Return(pos, expr)

	def analyze_if(self):
		pos = self.pos
		self.consume_keyword(kw.IF)
		conditionals = []
		emk = None
		while emk in (None, kw.ELIF):
			# condition
			with CriticalItem(self, "condition"):
				condition = self.analyze_expression()
			# then block
			self.consume_keyword(kw.THEN)
			then_block, emk, nextpos = self.analyze_statement_block(kw.ELIF, kw.ELSE, kw.END_IF)
			conditionals.append(statements.Conditional(pos, condition, then_block))
			pos = nextpos
		# else block
		if emk is kw.ELSE:
			else_block, _, _ = self.analyze_statement_block(kw.END_IF)
		else:
			else_block = None
		return statements.If(conditionals, else_block)

	def analyze_for(self):
		pos = self.pos
		self.consume_keyword(kw.FOR)
		# counter
		with CriticalItem(self, "compteur de la boucle"):
			counter = self.analyze_expression()
		# initial value
		self.consume_keyword(kw.FROM)
		with CriticalItem(self, "valeur initiale du compteur"):
			initial = self.analyze_expression()
		# final value
		self.consume_keyword(kw.TO)
		with CriticalItem(self, "valeur finale du compteur"):
			final = self.analyze_expression()
		# statement block
		self.consume_keyword(kw.DO)
		block, _, _ = self.analyze_statement_block(kw.END_FOR)
		return statements.For(pos, counter, initial, final, block)

	def analyze_while(self):
		pos = self.pos
		self.consume_keyword(kw.WHILE)
		# condition
		with CriticalItem(self, "condition de la boucle"):
			condition = self.analyze_expression()
		# statement block
		self.consume_keyword(kw.DO)
		block, _, _ = self.analyze_statement_block(kw.END_WHILE)
		return statements.While(pos, condition, block)

	def analyze_expression(self, root=True):
		with CriticalItem(self, "une expression"):
			lhs = self.analyze_primary_expression()
			bo1 = None
			with BacktrackFailure(self):
				bo1 = self.analyze_binary_operator()
			if bo1 is None:
				return lhs
			expr, bo2 = self.analyze_partial_expression(lhs, bo1)
			assert bo2 is None, "bo2 can't be an expression node here!"
			expr.root = root
			return expr

	def analyze_partial_expression(self, lhs, bo1, min_p=0):
		assert bo1 is None or isinstance(bo1, operators.BinaryOp)
		while bo1 is not None and bo1.precedence >= min_p:
			rhs = self.analyze_rhs(bo1)
			bo2 = None
			with BacktrackFailure(self):
				bo2 = self.analyze_binary_operator()
			# Keep extending bo1's RHS as long as the operators to the right (bo2) are
			# supposed to be part of its RHS (see BinaryOp.part_of_rhs
			# to see what this means)
			while bo2 is not None and bo2.part_of_rhs(bo1):
				rhs, bo2 = self.analyze_partial_expression(rhs, bo2, bo2.precedence)
			# At this point, either bo2 is an operator that's not supposed to be part
			# of bo1's RHS, or we hit a non-expression token (in which case bo2 is
			# None). Finish the bo1 node properly, and move onto bo2 if needed.
			bo1.lhs, bo1.rhs = lhs, rhs
			# Use bo1's node as the LHS for the next operator (bo2)
			lhs = bo1
			# Prepare next iteration
			bo1 = bo2
		# Return bo1's LHS (which is supposed to be an expression node in its own
		# right by now), and bo1 itself, which is a 'naked' operator (no LHS, no
		# RHS) with a low precedence or None if it's not an operator at all.
		return lhs, bo1

	def analyze_rhs(self, op):
		if not isinstance(op, operators.BinaryEncompassingOp):
			rhs = self.analyze_primary_expression()
		else:
			rhs = self.analyze_arglist(self.analyze_expression)
			self.consume_keyword(op.closing)
		return rhs

	def analyze_primary_expression(self):
		# check for sub-expression enclosed in parenthesis
		if self.consume_keyword(kw.LPAREN, soft=True):
			sub_expr = self.analyze_expression(False)
			self.consume_keyword(kw.RPAREN)
			return sub_expr
		# check for a unary operator
		try:
			uo = self.analyze_unary_operator()
		except syntax.ExpectedItem:
			pass
		else:
			# analyze primary after the unary operator
			uo.rhs = self.analyze_primary_expression()
			return uo
		# terminal
		return self.analyze_multiple("une expression primaire",
			self.analyze_literal_integer,
			self.analyze_literal_real,
			self.analyze_literal_string,
			self.analyze_literal_character,
			self.analyze_literal_boolean,
			self.analyze_identifier,)

	def analyze_binary_operator(self):
		return self.analyze_operator(operators.binary_flat)

	def analyze_unary_operator(self):
		return self.analyze_operator(operators.unary)

	def analyze_operator(self, op_list):
		pos = self.pos
		for op_class in op_list:
			if self.consume_keyword(op_class.keyword_def, soft=True):
				return op_class(pos)
		raise syntax.ExpectedItem(self.pos, "un opérateur")

	def analyze_arglist(self, analyze_arg, **kwargs):
		pos = self.pos
		arg_list = []
		has_next = True
		while has_next:
			arg = None
			arg_pos = self.pos
			with BacktrackFailure(self):
				arg = analyze_arg(**kwargs)
				arg_list.append(arg)
			has_next = self.consume_keyword(kw.COMMA, soft=True)
			if has_next and arg is None:
				raise syntax.SyntaxError(arg_pos, "argument vide")
		return arg_list

	def consume_regex(self, compiled_regex, advance=True, buf=None):
		if buf is None:
			buf = self.buf
		match = compiled_regex.match(self.buf, self.pos.char)
		try:
			string = match.group(0)
			if advance:
				self.advance(len(string))
			return string
		except AttributeError:
			raise syntax.ExpectedItem(self.pos, "regex non matchée")

	def analyze_literal_integer(self):
		pos = self.pos
		match = self.consume_regex(re_integer)
		return expression.LiteralInteger(pos, int(match))

	def analyze_literal_real(self):
		pos = self.pos
		match = self.consume_regex(re_real)
		return expression.LiteralReal(pos, float(match))

	def analyze_literal_string(self):
		pos = self.pos
		match = self.consume_regex(re_string, buf=self.raw_buf)
		return expression.LiteralString(pos, match[1:-1])

	def analyze_literal_character(self):
		pos = self.pos
		match = self.consume_regex(re_character, buf=self.raw_buf)
		return expression.LiteralCharacter(pos, match[1:-1])

	def analyze_literal_boolean(self):
		pos = self.pos
		true_kw = self.consume_keyword_choice(kw.TRUE, kw.FALSE)
		return expression.LiteralBoolean(pos, true_kw == kw.TRUE)

