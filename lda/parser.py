"""
LDA parser.
"""


import re
from .parsertools import BaseParser, Backtrack, CriticalItem, NotFoundHere, opening_keyword
from .errors import syntax
from . import kw
from . import expression
from . import operators
from . import statements
from . import types
from . import identifier
from .module import Module
from .function import Algorithm, Function
from .vardecl import VarDecl
from .lexicon import Lexicon


SCALARS_KW_TO_TYPE = {
	kw.INT    : types.INTEGER,
	kw.REAL   : types.REAL,
	kw.BOOL   : types.BOOLEAN,
	kw.CHAR   : types.CHARACTER,
	kw.STRING : types.STRING,
}


class Parser(BaseParser):
	"""
	LDA parser. This class contains the parsing logic specific to LDA's
	grammar.

	See the documentation for BaseParser (parsertools.py) to learn the behavior
	of analyze_ methods.
	"""

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

	def analyze_module(self):
		functions = []
		algorithms = []
		lexicon = Backtrack(self).give(self.analyze_lexicon)
		while not self.eof():
			with Backtrack(self):
				functions.append(self.analyze_function())
				continue
			with Backtrack(self):
				algorithms.append(self.analyze_algorithm())
				continue
			raise syntax.ExpectedItem(self.pos, "une fonction ou un algorithme",
					self.last_good_match)
		return Module(lexicon, functions, algorithms)

	def analyze_lexicon_and_body(self):
		# lexicon
		lexicon = Backtrack(self).give(self.analyze_lexicon)
		# statement block
		try:
			self.hardskip(kw.BEGIN)
		except syntax.ExpectedKeyword as e:
			if lexicon is None:
				e.tip = ("Si vous essayez de déclarer des variables, "
						"avez-vous pensé au mot-clé lexique ?")
			raise e
		body = self.analyze_statement_block()
		end_pos = self.pos
		self.hardskip(kw.END)
		return lexicon, body, end_pos

	@opening_keyword(kw.ALGORITHM)
	def analyze_algorithm(self, kwpos):
		lexicon, body, _ = self.analyze_lexicon_and_body()
		return Algorithm(kwpos, lexicon, body)

	@opening_keyword(kw.FUNCTION)
	def analyze_function(self, kwpos):
		# identifier
		ident = self.analyze_identifier(critical=True)
		# left parenthesis
		self.hardskip(kw.LPAREN)
		# formal parameters
		params = self.analyze_arglist(self.analyze_vardecl, kw.RPAREN, formal=True)
		# optional colon before return type (if omitted, no return type)
		if self.softskip(kw.COLON):
			with CriticalItem(self, "le type de retour de la fonction"):
				return_type = self.analyze_type_descriptor()
		else:
			return_type = types.VOID
		lexicon, body, end_pos = self.analyze_lexicon_and_body()
		return Function(kwpos, end_pos, ident, params, return_type, lexicon, body)

	@opening_keyword(kw.ARRAY)
	def analyze_array(self, kwpos):
		with CriticalItem(self, "le type des éléments du tableau"):
			element_type = self.analyze_non_array_type_descriptor()
		self.hardskip(kw.LSBRACK)
		with CriticalItem(self, "une dimension statique ou dynamique"):
			dimensions = self.analyze_arglist(self.analyze_array_dimension, kw.RSBRACK)
		return types.Array(kwpos, element_type, dimensions)

	def analyze_array_dimension(self):
		return self.analyze_either(
				self.analyze_static_array_dimension,
				self.analyze_dynamic_array_dimension)

	def analyze_static_array_dimension(self):
		return types.Array.StaticDimension(self.analyze_expression())

	@opening_keyword(kw.QUESTION_MARK)
	def analyze_dynamic_array_dimension(self, kwpos):
		return types.Array.DynamicDimension(kwpos)

	def analyze_type_descriptor(self):
		typedesc = Backtrack(self).give(self.analyze_array)
		if typedesc is None:
			typedesc = self.analyze_non_array_type_descriptor()
		return typedesc

	def analyze_non_array_type_descriptor(self):
		keyword = self.softskip(*SCALARS_KW_TO_TYPE.keys())
		try:
			return SCALARS_KW_TO_TYPE[keyword]
		except KeyError:
			return self.analyze_identifier(types.TypeAlias)

	def analyze_vardecl(self, ident=None, formal=False):
		if ident is None:
			ident = self.analyze_identifier(critical=True)
			self.hardskip(kw.COLON)
		inout = self.softskip(kw.INOUT)
		with CriticalItem(self, "le type de la variable"):
			typedesc = self.analyze_type_descriptor()
		return VarDecl(ident, typedesc, formal, inout)

	@opening_keyword(kw.LT)
	def analyze_composite(self, kwpos, ident):
		fields = self.analyze_arglist(self.analyze_vardecl, kw.GT)
		return types.Composite(ident, fields)

	@opening_keyword(kw.LEXICON)
	def analyze_lexicon(self, kwpos=None):
		variables = []
		composites = []
		while True:
			ident = Backtrack(self).give(self.analyze_identifier)
			if ident is None:
				break
			keyword = self.hardskip(kw.COLON, kw.EQ)
			if keyword == kw.COLON:
				variables.append(self.analyze_vardecl(ident=ident))
			elif keyword == kw.EQ:
				composites.append(self.analyze_composite(ident=ident))
		return Lexicon(variables, composites)

	def analyze_identifier(self, identifier_class=identifier.PureIdentifier, critical=False):
		"""
		If `critical` is True, IllegalIdentifier or ReservedWord will be raised
		instead of NotFoundHere if no valid identifier is found. This is
		especially useful wherever an identifier is absolutely required (for
		example, to denote a function's name in a function header).

		However, non-critical identifiers are more suitable to places like
		expressions, where the identifiers are supposed to refer to symbols
		declared elsewhere.
		"""
		if not critical:
			try:
				return self.analyze_identifier(identifier_class=identifier_class, critical=True)
			except syntax.SyntaxError:
				raise NotFoundHere
		else:
			pos = self.pos
			try:
				name = self.analyze_regex(self.re_identifier, advance=False)
			except NotFoundHere:
				raise syntax.IllegalIdentifier(pos)
			if name in kw.reserved:
				raise syntax.ReservedWord(pos, name)
			self.advance(len(name))
			return identifier_class(pos, name)

	def analyze_statement_list(self):
		block = []
		while True:
			with Backtrack(self):
				unit = self.analyze_statement()
				block.append(unit)
				continue
			break
		return block

	def analyze_statement_block(self):
		pos = self.pos
		return statements.StatementBlock(pos, self.analyze_statement_list())

	def analyze_statement(self):
		# First, try statements that start with a keyword.
		with Backtrack(self):
			return self.analyze_either(
					self.analyze_return,
					self.analyze_if,
					self.analyze_for,
					self.analyze_while)
		# Assignments and function calls are the only statements that start
		# with an expression. We're going to avoid parsing an expression twice.
		expr = self.analyze_expression()
		op_pos = self.pos
		if self.softskip(kw.ASSIGN):
			# expr is the lefthand side of an assignment statement
			rhs = self.analyze_expression()
			return statements.Assignment(op_pos, expr, rhs)
		elif isinstance(expr, operators.FunctionCall):
			# expr is a standalone function call, not followed by the
			# ASSIGN operator. (If it was followed by ASSIGN, it'd be
			# parsed as an assignment statement and the semantic analysis
			# would fail later on)
			return statements.FunctionCallWrapper(expr)
		else:
			# expr is a standalone expression, but we can't treat it as a
			# statement since its result is discarded.
			if expr.compound:
				raise syntax.DiscardedExpression(expr)
			else:
				# Non-compound expression, i.e. it is made of a single token.
				# Raising NotFoundHere instead of DiscardedExpression may help
				# reporting a stray token in one of the calling methods.
				raise NotFoundHere

	@opening_keyword(kw.RETURN)
	def analyze_return(self, kwpos):
		expr = Backtrack(self).give(self.analyze_expression)
		return statements.Return(kwpos, expr)

	@opening_keyword(kw.IF)
	def analyze_if(self, kwpos):
		conditionals = []
		keyword = None
		pos = self.pos
		while keyword in (None, kw.ELIF):
			# condition
			with CriticalItem(self, "la condition de la clause"):
				condition = self.analyze_expression()
			# then block
			self.hardskip(kw.THEN)
			then_body = self.analyze_statement_list()
			keyword = self.hardskip(kw.ELIF, kw.ELSE, kw.END_IF)
			conditionals.append(statements.Conditional(pos, condition, then_body))
			pos = self.pos
		# else block
		if keyword is kw.ELSE:
			else_block = self.analyze_statement_block()
			self.hardskip(kw.END_IF)
		else:
			else_block = None
		return statements.If(conditionals, else_block)

	@opening_keyword(kw.FOR)
	def analyze_for(self, kwpos):
		# counter
		with CriticalItem(self, "le compteur de la boucle"):
			counter = self.analyze_expression()
		# initial value
		self.hardskip(kw.FROM)
		with CriticalItem(self, "la valeur initiale du compteur"):
			initial = self.analyze_expression()
		# final value
		self.hardskip(kw.TO)
		with CriticalItem(self, "la valeur finale du compteur"):
			final = self.analyze_expression()
		# statement block
		self.hardskip(kw.DO)
		body = self.analyze_statement_list()
		self.hardskip(kw.END_FOR)
		return statements.For(kwpos, counter, initial, final, body)

	@opening_keyword(kw.WHILE)
	def analyze_while(self, kwpos):
		# condition
		with CriticalItem(self, "la condition de la boucle"):
			condition = self.analyze_expression()
		# statement block
		self.hardskip(kw.DO)
		body = self.analyze_statement_list()
		self.hardskip(kw.END_WHILE)
		return statements.While(kwpos, condition, body)

	def analyze_expression(self, root=True):
		lhs = self.analyze_primary_expression()
		# try to find a binary operator
		nbo1 = Backtrack(self).give(self.analyze_naked_binary_operator)
		if nbo1 is None:
			return lhs
		expr, nbo2 = self.analyze_partial_expression(lhs, nbo1)
		assert nbo2 is None, "expression complete but an operator is still pending!"
		expr.root = root
		return expr

	def analyze_partial_expression(self, lhs, nbo1, min_p=0):
		if nbo1 is not None:
			assert isinstance(nbo1, operators.NakedOperator)
			assert issubclass(nbo1.cls, operators.BinaryOp)
		while nbo1 is not None and nbo1.cls.precedence >= min_p:
			# Parse the righthand-side operand of the first operator.
			try:
				if issubclass(nbo1.cls, operators.BinaryEncompassingOp):
					rhs = self.analyze_arglist(self.analyze_expression, nbo1.cls.closing)
				else:
					rhs = self.analyze_primary_expression()
			except NotFoundHere:
				raise syntax.MissingRightOperand(nbo1.pos)
			# Parse the next operator, if any.
			nbo2 = Backtrack(self).give(self.analyze_naked_binary_operator)
			# Keep extending bo1's RHS as long as the operators to the right (bo2) are
			# supposed to be part of its RHS (see BinaryOp.part_of_rhs
			# to see what this means)
			while nbo2 is not None and nbo2.cls.part_of_rhs(nbo1.cls):
				rhs, nbo2 = self.analyze_partial_expression(
						rhs, nbo2, nbo2.cls.precedence)
			# At this point, either bo2 is an operator that's not supposed to
			# be part of bo1's RHS, or we hit a non-expression token (in which
			# case bo2 is None).
			# Finish building the first binary operator and use it as the
			# lefthand-side operand for the next operator.
			lhs = nbo1.build(lhs, rhs)
			# Prepare next iteration
			nbo1 = nbo2
		# Return bo1's LHS (which is supposed to be an expression node in its own
		# right by now), and bo1 itself, which is a 'naked' operator (no LHS, no
		# RHS) with a low precedence or None if it's not an operator at all.
		return lhs, nbo1

	def analyze_primary_expression(self):
		# check for sub-expression enclosed in parenthesis
		if self.softskip(kw.LPAREN):
			sub_expr = self.analyze_expression(False)
			self.hardskip(kw.RPAREN)
			return sub_expr
		# check for a unary operator
		nuo = Backtrack(self).give(self.analyze_naked_operator, operators.unary)
		if nuo is not None:
			# analyze unary operator's operand, which is a primary expression
			try:
				rhs = self.analyze_primary_expression()
			except NotFoundHere:
				raise syntax.MissingRightOperand(nuo.pos)
			return nuo.build(rhs)
		# terminal
		with Backtrack(self):
			return self.analyze_identifier(expression.ExpressionIdentifier)
		return self.analyze_either(
				self.analyze_literal_integer,
				self.analyze_literal_real,
				self.analyze_literal_string,
				self.analyze_literal_character,
				self.analyze_literal_boolean)

	def analyze_naked_binary_operator(self):
		return self.analyze_naked_operator(operators.binary_flat)

	def analyze_naked_operator(self, op_list):
		pos = self.pos
		for op_class in op_list:
			if self.softskip(op_class.keyword_def):
				return operators.NakedOperator(pos, op_class)
		raise NotFoundHere

	def analyze_arglist(self, analyze_arg, closing_kw, **kwargs):
		if self.softskip(closing_kw):
			# Got the closing keyword right away: empty arglist.
			return []
		arglist = []
		has_next = True
		while has_next:
			pos = self.pos
			# When parsing a critical identifier, a SyntaxError is returned if
			# there is no identifier. Putting an aaditional comma check here
			# allows us to raise a friendlier error message in that case.
			if self.softskip(kw.COMMA):
				raise syntax.SyntaxError(pos, "argument vide")
			try:
				arglist.append(analyze_arg(**kwargs))
			except NotFoundHere:
				raise syntax.SyntaxError(pos, "argument vide")
			has_next = self.softskip(kw.COMMA)
		# Even though there cannot be a comma here (since has_next went False),
		# we're hardskipping kw.COMMA anyway. That way, in case of an error,
		# the user knows they could've used a comma here.
		self.hardskip(closing_kw, kw.COMMA)
		return arglist

	def analyze_literal_integer(self):
		pos = self.pos
		match = self.analyze_regex(self.re_integer)
		return expression.LiteralInteger(pos, int(match))

	def analyze_literal_real(self):
		pos = self.pos
		match = self.analyze_regex(self.re_real)
		return expression.LiteralReal(pos, float(match))

	def analyze_literal_string(self):
		pos = self.pos
		# Retain case: match raw_buf, not buf
		match = self.analyze_regex(self.re_string, buf=self.raw_buf)
		return expression.LiteralString(pos, match[1:-1])

	@opening_keyword(kw.QUOTE1)
	def analyze_literal_character(self, kwpos):
		if self.softskip(kw.QUOTE1):
			raise syntax.SyntaxError(kwpos, "un caractère ne peut pas être vide")
		if self.eof():
			raise syntax.UnclosedItem(kwpos, "guillemet non fermé")
		char = self.raw_buf[self.pos.char]
		self.advance(1)
		if not self.softskip(kw.QUOTE1):
			e = syntax.SyntaxError(kwpos,
					"un seul caractère est admis entre guillemets simples")
			e.tip = ("Si vous voulez définir une chaîne, entourez-la de "
					"double-guillemets (\"). Les guillemets simples (') "
					"sont réservés aux caractères.")
			raise e
		return expression.LiteralCharacter(kwpos, char)

	def analyze_literal_boolean(self):
		pos = self.pos
		keyword = self.softskip(kw.TRUE, kw.FALSE)
		if keyword is None:
			raise NotFoundHere
		return expression.LiteralBoolean(pos, keyword == kw.TRUE)

