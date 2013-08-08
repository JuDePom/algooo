import re
import keywords as kw
import operators
import module
import tokens
import typedef
import position
import expression
import statements
import symboltable
from errors import *

re_identifier = re.compile(r'[^\d\W]\w*')

# match at least one digit;
# must NOT followed by a single dot, an alpha, or a _
re_integer    = re.compile(r'\d+(?![\w\.]($|[^\.]))')

# match at least one digit, one dot, and zero or more digits,
# **OR** match one dot, and at least one digit;
# but either match must NOT be followed by a single dot, an alpha, or a _
re_real       = re.compile(r'(\d+\.\d*|\.\d+)(?![\w\.]($|[^\.]))')

re_string     = re.compile(r'".*?"') # TODO- escaping

class Parser:
	'''
	LDA parser. Builds up an AST from LDA source code.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. If the item was found, the current position
	in the buffer is moved past the end of the item, and True is returned.
	Otherwise, the current position is left untouched, and None is returned.
	These functions may raise an exception if a syntax error was found.
	'''

	def __init__(self, path, buf=None):
		if path is not None:
			self.path = path
			with open(path, 'rt', encoding='utf8') as input_file:
				self.buf = input_file.read()
		else:
			self.path = "<direct>"
			self.buf = buf
		self.buflen = len(self.buf)
		self.reset_pos()

	def reset_pos(self):
		self.pos = position.Position(self.path)

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

	def analyze_module(self):
		self.advance()
		functions = []
		algorithm = None
		has_algorithm = False
		while not self.eof():
			function = self.analyze_function()
			if function is not None:
				functions.append(function)
				continue
			algorithm = self.analyze_algorithm()
			if algorithm is not None:
				if has_algorithm:
					raise LDASyntaxError(self.pos,
							"Il ne peut y avoir qu'un seul algorithme par module")
				has_algorithm = True
				continue
			raise ExpectedItemError(self.pos, "une fonction ou un algorithme")
			# TODO : ... ou une def de composite ?
		return module.Module(functions, algorithm)

	def analyze_algorithm(self):
		pos0 = self.pos
		if not self.find_keyword(kw.ALGORITHM):
			return
		# point of no-return
		# lexicon
		lexi = self.analyze_lexicon()
		# statement block
		self.find_keyword(kw.BEGIN, mandatory=True)
		body, _ = self.analyze_statement_block(kw.END)
		return module.Algorithm(pos0, lexi, body)

	def analyze_function(self):
		pos0 = self.pos
		if not self.find_keyword(kw.FUNCTION):
			return
		# point of no-return
		# identifier
		ident = self.analyze_identifier()
		if ident is None:
			raise IllegalIdentifier(self.pos)
		# mandatory left parenthesis
		self.find_keyword(kw.LPAREN, mandatory=True)
		# formal parameters, or lack thereof
		if self.find_keyword(kw.RPAREN):
			# got an RPAREN right away: empty parameter list
			params = []
		else:
			# non-empty parameter list
			params = self.analyze_varargs(self.analyze_variable_declaration)
			self.find_keyword(kw.RPAREN, mandatory=True)
		# optional colon before return type (if omitted, no return type)
		if self.find_keyword(kw.COLON):
			raise NotImplementedError("type de retour de la fonction")
		# lexicon
		lexi = self.analyze_lexicon()
		# statement block
		self.find_keyword(kw.BEGIN, mandatory=True)
		body, _ = self.analyze_statement_block(kw.END)
		return module.Function(start_kw.pos, ident, params, lexi, body)

	def analyze_variable_declaration(self):
		pos0 = self.pos
		# identifier
		ident = self.analyze_identifier()
		if ident is None:
			return
		# inout
		is_inout = self.find_keyword(kw.INOUT)
		# mandatory colon (but if we don't find one, it might be a composite,
		# so don't raise an exception)
		if not self.find_keyword(kw.COLON):
			self.pos = pos0
			return
		# array
		is_array = self.find_keyword(kw.ARRAY)
		# enclosed type
		type_word = None
		for candidate in typedef.scalars:
			if self.find_keyword(candidate.type_word):
				type_word = candidate
				break
		else:
			type_word = self.analyze_identifier()
		if type_word is None:
			raise ExpectedItemError(self.pos, "un type scalaire ou composite")
		# array dimensions
		if is_array:
			self.find_keyword(kw.LSBRACK, mandatory=True)
			array_dimensions = self.analyze_varargs(self.analyze_expression)
			self.find_keyword(kw.RSBRACK, mandatory=True)
		else:
			array_dimensions = None
		return symboltable.VariableDeclaration(ident, is_inout, type_word, array_dimensions)

	def analyze_lexicon(self):
		pos0 = self.pos
		if not self.find_keyword(kw.LEXICON):
			return
		variables = []
		composites = []
		while True:
			v = self.analyze_variable_declaration()
			if v is not None:
				variables.append(v)
				continue
			c = self.analyze_composite()
			if c is not None:
				composites.append(c)
				continue
			break
		return symboltable.Lexicon(pos0, variables, composites)

	def analyze_identifier(self):
		match = re_identifier.match(self.buf, self.pos.char)
		if match is None:
			return
		identifier = match.group(0)
		if identifier in kw.meta.all_keywords:
			return # invalid identifier if the string is a keyword
		pos0 = self.pos
		self.advance(len(identifier))
		return tokens.Identifier(pos0, identifier)

	def find_keyword(self, keyword, mandatory=False):
		pos0 = self.pos
		found_string = keyword.find(self.buf, self.pos.char)
		if found_string is not None:
			self.advance(len(found_string))
			return True
		if mandatory:
			raise ExpectedKeywordError(self.pos, keyword)

	def analyze_composite(self):
		pos0 = self.pos
		ident = self.analyze_identifier()
		if ident is None:
			return
		if not self.find_keyword(kw.EQ):
			self.pos = pos0
			return
		# point of no return
		self.find_keyword(kw.LT, mandatory=True)
		fp_list = self.analyze_varargs(self.analyze_variable_declaration)
		self.find_keyword(kw.GT, mandatory=True)
		return symboltable.Composite(ident, fp_list)

	def analyze_statement_block(self, *end_marker_keywords):
		pos0 = self.pos
		block = []
		unit = self.analyze_statement()
		while unit is not None:
			block.append(unit)
			unit = self.analyze_statement()
		for marker in end_marker_keywords:
			if self.find_keyword(marker):
				return statements.StatementBlock(pos0, block), marker
		raise ExpectedKeywordError(self.pos, *end_marker_keywords)

	def analyze_multiple(self, *analysis_order):
		for thing in (analyze() for analyze in analysis_order):
			if thing is not None:
				return thing

	def analyze_statement(self):
		return self.analyze_multiple(
			self.analyze_expression,
			self.analyze_if,
			self.analyze_for,
			self.analyze_while,
			self.analyze_do_while)

	def analyze_if(self):
		pos0 = self.pos
		if not self.find_keyword(kw.IF):
			return
		# point of no return
		# condition
		condition = self.analyze_expression()
		if condition is None:
			raise ExpectedItemError(self.pos, "condition")
		# then block
		self.find_keyword(kw.THEN, mandatory=True)
		then_block, emk = self.analyze_statement_block(kw.ELSE, kw.END_IF)
		# else block
		if emk is kw.ELSE:
			else_block, _ = self.analyze_statement_block(kw.END_IF)
		else:
			else_block = None
		return IfThenElse(pos0, condition, then_block, else_block)

	def analyze_for(self):
		pos0 = self.pos
		if not self.find_keyword(kw.FOR):
			return
		# point of no return
		# counter
		counter = self.analyze_identifier()
		if counter is None:
			raise ExpectedItemError(self.pos, "compteur de la boucle")
		# initial value
		self.find_keyword(kw.FROM, mandatory=True)
		initial = self.analyze_expression()
		if initial is None:
			raise ExpectedItemError(self.pos, "valeur de départ du compteur")
		# final value
		self.find_keyword(kw.TO, mandatory=True)
		final = self.analyze_expression()
		if final is None:
			raise ExpectedItemError(self.pos, "valeur finale du compteur")
		# statement block
		self.find_keyword(kw.DO, mandatory=True)
		block, _ = self.analyze_statement_block(kw.END_FOR)
		return statements.For(pos0, counter, initial, final, block)

	def analyze_while(self):
		pos0 = self.pos
		if not self.find_keyword(kw.WHILE):
			return
		# point of no return
		# condition
		condition = self.analyze_expression()
		if condition is None:
			raise ExpectedItemError(self.pos, "condition de la boucle")
		# statement block
		self.find_keyword(kw.DO, mandatory=True)
		block, _ = self.analyze_statement_block(kw.END_WHILE)
		return statements.While(pos0, condition, block)

	def analyze_do_while(self):
		pos0 = self.pos
		if not self.find_keyword(kw.DO):
			return
		# point of no return
		# statement block
		block, _ = self.analyze_statement_block(kw.TO)
		# condition
		condition = self.analyze_expression()
		if condition is None:
			raise ExpectedItemError(self.pos, "condition de la boucle")
		return statements.DoWhile(pos0, block, condition)

	def analyze_expression(self):
		lhs = self.analyze_primary_expression()
		bo1 = self.analyze_binary_operator()
		expr, bo2 = self.analyze_partial_expression(lhs, bo1)
		assert bo2 is None, "bo2 can't be an expression node here!"
		return expr

	def analyze_partial_expression(self, lhs, bo1, min_p=0):
		assert bo1 is None or isinstance(bo1, operators.BinaryOp)
		while bo1 is not None and bo1.precedence >= min_p:
			rhs = self.analyze_rhs(bo1)
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
			self.find_keyword(op.encompass_varargs_till, mandatory=True)
		return rhs

	def analyze_primary_expression(self):
		# check for sub-expression enclosed in parenthesis
		if self.find_keyword(kw.LPAREN):
			sub_expr = self.analyze_expression()
			self.find_keyword(kw.RPAREN, mandatory=True)
			return sub_expr
		# check for a unary operator
		uo = self.analyze_unary_operator()
		if uo is not None:
			# analyze primary after the unary operator
			uo.rhs = self.analyze_primary_expression()
			return uo
		# terminal symbol
		return self.analyze_multiple(
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
		pos0 = self.pos
		for op_class in op_list:
			if self.find_keyword(op_class.keyword_def):
				return op_class(pos0)

	def analyze_varargs(self, analyze_arg):
		pos0 = self.pos
		arg_list = []
		next_arg = True
		while next_arg:
			arg = analyze_arg()
			if arg is not None:
				arg_list.append(arg)
			next_arg = self.find_keyword(kw.COMMA)
			if next_arg and arg is None:
				raise LDASyntaxError(self.pos, "argument vide")
		return expression.Varargs(pos0, arg_list)

	def analyze_literal(self, compiled_regexp, literal_class, converter):
		pos0 = self.pos
		match = compiled_regexp.match(self.buf, self.pos.char)
		if match is not None:
			string = match.group(0)
			self.advance(len(string))
			return literal_class(pos0, converter(string))

	def analyze_literal_boolean(self):
		pos0 = self.pos
		value = self.find_keyword(kw.TRUE)
		if not value and not self.find_keyword(kw.FALSE):
			return
		return expression.LiteralBoolean(pos0, value)

