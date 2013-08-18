import re
from . import keywords as kw
from . import module
from . import position
from . import expression
from . import operators
from . import statements
from . import typedesc
from .errors import *

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
	(?![\.\w]) # The last digit may not be followed by another dot
	           # or a "word" character.
	''', re.VERBOSE)

re_string = re.compile(r'".*?"') # TODO- escaping

class ParserContextManager:
	def __init__(self, parser):
		self.parser = parser
	
	def __enter__(self):
		self.pos = self.parser.pos
	
	def __exit__(self, exc_type, exc_value, traceback):
		if isinstance(exc_value, LDASyntaxError):
			self.parser.append_syntax_error(exc_value)
			self.syntax_error(exc_value)
			# Don't let the exception propagate if we got here.
			return True
		else:
			# Unknown error. Let Python handle it.
			return False

class BacktrackFailure(ParserContextManager):
	def syntax_error(self, exc_value):
		self.parser.pos = self.pos

class CriticalItem(ParserContextManager):
	def __init__(self, parser, expected_item_name=None):
		super().__init__(parser)
		self.expected_item_name = expected_item_name

	def syntax_error(self, exc_value):
		raise ExpectedItemError(self.pos, self.expected_item_name)

class Parser:
	'''
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and True is returned.
	Otherwise, the current position is left untouched, and None is returned.
	These functions may raise an exception if a syntax error was found.
	'''

	def __init__(self, path=None, buf=""):
		if path is not None:
			self.path = path
			with open(path, 'rt', encoding='utf8') as input_file:
				self.set_buf(input_file.read())
		else:
			self.path = "<direct>"
			self.set_buf(buf)

	def reset_pos(self):
		self.pos = position.Position(self.path)

	def set_buf(self, value):
		self.syntax_errors = []
		self.buf = value
		self.buflen = len(self.buf)
		self.reset_pos()
		self.advance()

	def append_syntax_error(self, new_error):
		if not self.syntax_errors or new_error.pos > self.syntax_errors[-1].pos:
			self.syntax_errors = [new_error]
		elif new_error.pos == self.syntax_errors[-1].pos:
			self.syntax_errors.append(new_error)

	def advance(self, chars=0):
		'''
		Advance current position in the buffer so that the cursor points on something
		significant (i.e. no whitespace, no comments)

		This function must be called at the very beginning of a source file, and
		after every operation that permanently consumes bytes from the buffer.
		'''
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

	def consume_keyword(self, keyword, soft=False):
		found_string = keyword.find(self.buf, self.pos.char)
		if found_string is None:
			if not soft:
				raise ExpectedKeywordError(self.pos, keyword)
			else:
				return False
		self.advance(len(found_string))
		return True

	def consume_keyword_choice(self, *choices):
		for keyword in choices:
			if self.consume_keyword(keyword, soft=True):
				return keyword
		raise ExpectedKeywordError(self.pos, *choices)

	def analyze_multiple(self, group_name, *analysis_order):
		for analyze in analysis_order:
			with BacktrackFailure(self):
				return analyze()
		raise ExpectedItemError(self.pos, group_name)

	def analyze_module(self):
		functions = []
		algorithm = None
		has_algorithm = False
		while not self.eof():
			with BacktrackFailure(self):
				functions.append(self.analyze_function())
				continue
			with BacktrackFailure(self):
				algorithm = self.analyze_algorithm()
				if has_algorithm:
					raise LDASyntaxError(self.pos,
							"Il ne peut y avoir qu'un seul algorithme par module")
				has_algorithm = True
				continue
			raise ExpectedItemError(self.pos, "une fonction ou un algorithme")
			# TODO : ... ou une def de composite ?
		return module.Module(functions, algorithm)

	def analyze_algorithm(self):
		pos = self.pos
		self.consume_keyword(kw.ALGORITHM)
		# lexicon
		lexicon = self.analyze_lexicon()
		# statement block
		self.consume_keyword(kw.BEGIN)
		body, _ = self.analyze_statement_block(kw.END)
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
			params = self.analyze_varargs(self.analyze_field)
			self.consume_keyword(kw.RPAREN)
		# optional colon before return type (if omitted, no return type)
		if self.consume_keyword(kw.COLON, soft=True):
			with CriticalItem(self, "type de retour de la fonction"):
				return_type = self.analyze_type_descriptor()
		else:
			return_type = typedesc.Void
		# lexicon
		lexicon = None
		with BacktrackFailure(self):
			lexicon = self.analyze_lexicon()
		# statement block
		self.consume_keyword(kw.BEGIN)
		body, _ = self.analyze_statement_block(kw.END)
		return module.Function(pos, ident, params, return_type, lexicon, body)

	def analyze_scalar_type(self):
		scalars = {
				kw.INT    : typedesc.Integer,
				kw.REAL   : typedesc.Real,
				kw.BOOL   : typedesc.Boolean,
				kw.CHAR   : typedesc.Character,
				kw.STRING : typedesc.String,
		}
		with CriticalItem(self, "un type scalaire"):
			scalar_kw = self.consume_keyword_choice(*scalars.keys())
			return scalars[scalar_kw]

	def analyze_array_type(self):
		self.consume_keyword(kw.ARRAY)
		element_type = self.analyze_type_descriptor()
		self.consume_keyword(kw.LSBRACK)
		dimensions = self.analyze_varargs(self.analyze_expression)
		self.consume_keyword(kw.RSBRACK)
		return typedesc.ArrayType(element_type, dimensions)

	def analyze_type_alias(self):
		alias_id = self.analyze_identifier()
		return typedesc.TypeAlias(alias_id)

	def analyze_type_descriptor(self):
		with BacktrackFailure(self):
			return self.analyze_array_type()
		with BacktrackFailure(self):
			return self.analyze_scalar_type()
		with BacktrackFailure(self):
			return self.analyze_type_alias()
		raise ExpectedItemError(self.pos, "un descripteur de type")

	def analyze_field(self):
		ident = self.analyze_identifier()
		self.consume_keyword(kw.COLON)
		type_descriptor = self.analyze_type_descriptor()
		return typedesc.Field(ident, type_descriptor)

	def analyze_composite_declaration(self):
		ident = self.analyze_identifier()
		self.consume_keyword(kw.EQ)
		self.consume_keyword(kw.LT)
		field_list = self.analyze_varargs(self.analyze_field)
		self.consume_keyword(kw.GT)
		return typedesc.CompositeType(ident, field_list)

	def analyze_lexicon(self):
		self.consume_keyword(kw.LEXICON)
		variables = {}
		composites = {}
		while True:
			with BacktrackFailure(self):
				v = self.analyze_field()
				variables[v.name] = v.type_descriptor
				continue
			with BacktrackFailure(self):
				c = self.analyze_composite_declaration()
				composites[c.name] = c
				continue
			break
		return typedesc.Lexicon(variables, composites)

	def analyze_identifier(self):
		match = re_identifier.match(self.buf, self.pos.char)
		if match is None:
			raise IllegalIdentifier(self.pos)
		name = match.group(0)
		if name in kw.meta.all_keywords:
			raise ReservedWord(self.pos, name)
		pos = self.pos
		self.advance(len(name))
		return typedesc.Identifier(pos, name)

	def analyze_statement_block(self, *end_marker_keywords):
		pos = self.pos
		block = []
		while True:
			with BacktrackFailure(self):
				unit = self.analyze_statement()
				block.append(unit)
				continue
			break
		marker = self.consume_keyword_choice(*end_marker_keywords)
		return statements.StatementBlock(pos, block), marker

	def analyze_statement(self):
		return self.analyze_multiple("une instruction",
			self.analyze_expression,
			self.analyze_if,
			self.analyze_for,
			self.analyze_while,)

	def analyze_if(self):
		pos = self.pos
		self.consume_keyword(kw.IF)
		# condition
		with CriticalItem(self, "condition"):
			condition = self.analyze_expression()
		# then block
		self.consume_keyword(kw.THEN)
		then_block, emk = self.analyze_statement_block(kw.ELSE, kw.END_IF)
		# else block
		if emk is kw.ELSE:
			else_block, _ = self.analyze_statement_block(kw.END_IF)
		else:
			else_block = None
		return statements.IfThenElse(pos, condition, then_block, else_block)

	def analyze_for(self):
		pos = self.pos
		self.consume_keyword(kw.FOR)
		# counter
		with CriticalItem(self, "compteur de la boucle"):
			counter = self.analyze_identifier()
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
		block, _ = self.analyze_statement_block(kw.END_FOR)
		return statements.For(pos, counter, initial, final, block)

	def analyze_while(self):
		pos = self.pos
		self.consume_keyword(kw.WHILE)
		# condition
		with CriticalItem(self, "condition de la boucle"):
			condition = self.analyze_expression()
		# statement block
		self.consume_keyword(kw.DO)
		block, _ = self.analyze_statement_block(kw.END_WHILE)
		return statements.While(pos, condition, block)

	def analyze_expression(self):
		with CriticalItem(self, "une expression"):
			lhs = self.analyze_primary_expression()
			bo1 = None
			with BacktrackFailure(self):
				bo1 = self.analyze_binary_operator()
			if bo1 is None:
				return lhs
			expr, bo2 = self.analyze_partial_expression(lhs, bo1)
			assert bo2 is None, "bo2 can't be an expression node here!"
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
			if rhs is None:
				raise LDASyntaxError(self.pos, "cet opérateur binaire requiert "
						"une opérande à sa droite")
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
		if op.encompass_varargs_till is None:
			rhs = self.analyze_primary_expression()
		else:
			rhs = self.analyze_varargs(self.analyze_expression)
			self.consume_keyword(op.encompass_varargs_till)
		return rhs

	def analyze_primary_expression(self):
		# check for sub-expression enclosed in parenthesis
		if self.consume_keyword(kw.LPAREN, soft=True):
			sub_expr = self.analyze_expression()
			self.consume_keyword(kw.RPAREN)
			return sub_expr
		# check for a unary operator
		try:
			uo = self.analyze_unary_operator()
		except ExpectedItemError:
			pass
		else:
			# analyze primary after the unary operator
			uo.rhs = self.analyze_primary_expression()
			return uo
		# terminal symbol
		return self.analyze_multiple("une expression primaire",
			lambda: self.analyze_literal(re_integer, expression.LiteralInteger, int),
			lambda: self.analyze_literal(re_real, expression.LiteralReal, float),
			lambda: self.analyze_literal(re_string, expression.LiteralString, lambda s: s[1:-1]),
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
		raise ExpectedItemError(self.pos, "un opérateur")

	def analyze_varargs(self, analyze_arg):
		pos = self.pos
		arg_list = []
		arg = None
		has_next = True
		while has_next:
			with BacktrackFailure(self):
				arg = analyze_arg()
				arg_list.append(arg)
			has_next = self.consume_keyword(kw.COMMA, soft=True)
			if has_next and arg is None:
				raise LDASyntaxError(self.pos, "argument vide")
		return expression.Varargs(pos, arg_list)

	def analyze_literal(self, compiled_regexp, literal_class, converter):
		pos = self.pos
		match = compiled_regexp.match(self.buf, self.pos.char)
		if match is not None:
			string = match.group(0)
			self.advance(len(string))
			return literal_class(pos, converter(string))
		raise ExpectedItemError(self.pos, "un littéral de la classe " + str(literal_class))

	def analyze_literal_boolean(self):
		with CriticalItem(self, "un booléen littéral"):
			pos = self.pos
			true_kw = self.consume_keyword_choice(kw.TRUE, kw.FALSE)
			return expression.LiteralBoolean(pos, true_kw == kw.TRUE)
