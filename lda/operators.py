from .expression import Expression, surround, nonwritable
from .errors import semantic
from . import types
from . import kw
from . import semantictools

#######################################################################
#
# HELPER CLASSES
#
#######################################################################

class NakedOperator:
	"""
	Container for a position and an operator class.

	Meant for temporary use by the parser during the parsing of an operator.
	When the parser has finished parsing all components of an operator, i.e.
	the operator token and its operands, it should call build() to create a
	proper operator object.

	Instances of NakedOperator must not be placed into the AST!
	"""

	def __init__(self, pos, cls):
		self.pos = pos
		self.cls = cls

	def build(self, *args, **kwargs):
		return self.cls(self.pos, *args, **kwargs)

#######################################################################
#
# GENERIC OPERATOR BASE CLASSES
#
#######################################################################

class UnaryOp(Expression):
	"""
	Unary operator.

	Right-associative, non-writable, and non-terminal by default (these
	properties can be overridden). See Expression's docstring for info about
	writable and terminal.

	Has a righthand-side operand only.
	"""

	right_ass = True
	terminal = False

	def __init__(self, pos, rhs):
		super().__init__(pos)
		self.rhs = rhs

	def __eq__(self, other):
		return type(self) == type(other) and self.rhs == other.rhs

	@surround
	def lda(self, pp):
		pp.put(self.keyword_def, " ", self.rhs)

	@surround
	def js(self, pp):
		pp.put(self.js_kw, " ", self.rhs)

class BinaryOp(Expression):
	"""
	Binary operator. Has a lefthand-side operand and a righthand-side operand.

	Default properties (can be overridden):
	- left-associative,
	- non-writable (see Expression),
	- non-terminal (see Expression),
	- non-encompassing.

	A binary operator may be 'encompassing'; that is, its RHS is a list of
	zero or more parameters delimited by commas and closed with a complementary
	keyword. To declare an operator encompassing, define the `closing`
	attribute to the keyword that closes the list of parameters.
	"""

	right_ass = False
	terminal = False

	def __init__(self, pos, lhs, rhs):
		super().__init__(pos)
		self.lhs = lhs
		self.rhs = rhs

	def __eq__(self, other):
		return type(self) == type(other) and \
				self.lhs == other.lhs and \
				self.rhs == other.rhs

	@classmethod
	def part_of_rhs(cls, whose):
		return cls.precedence > whose.precedence or \
			(cls.right_ass and cls.precedence == whose.precedence)

	@surround
	def lda(self, pp):
		pp.put(self.lhs, " ", self.keyword_def, " ", self.rhs)

	@surround
	def js(self, pp):
		pp.put(self.lhs, " ", self.js_kw, " ", self.rhs)

#######################################################################
#
# SPECIFIC OPERATOR BASE CLASSES
#
#######################################################################

class UnaryNumberOp(UnaryOp):
	"""
	Unary operator that can only be used with a number type.
	"""
	@nonwritable
	def check(self, context, logger):
		self.rhs.check(context, logger)
		rtype = self.rhs.resolved_type
		if rtype not in (types.INTEGER, types.REAL):
			logger.log(semantic.TypeError(self.pos, "cet opérateur unaire "
					"ne peut être appliqué qu'à un nombre entier ou réel",
					rtype))
			self.resolved_type = types.ERRONEOUS
		else:
			self.resolved_type = rtype

	@surround
	def lda(self, pp):
		pp.put(self.keyword_def, self.rhs)
	
	@surround
	def js(self, pp):
		pp.put(self.js_kw, self.rhs)

class BinaryChameleonOp(BinaryOp):
	"""
	Binary operator taking operands of equivalent types. The type of the operator
	is determined by the strongest type among the operands.
	"""
	@nonwritable
	def check(self, context, logger):
		self.lhs.check(context, logger)
		self.rhs.check(context, logger)
		ltype, rtype = self.lhs.resolved_type, self.rhs.resolved_type
		strongtype = ltype.equivalent(rtype)
		if strongtype is None:
			logger.log(semantic.TypeMismatch(self.pos, "les types des opérandes "
					"doivent être équivalents", ltype, rtype))
			self.resolved_type = types.ERRONEOUS
		else:
			self.resolved_type = strongtype

class BinaryPolymorphicOp(BinaryOp):
	"""
	Operator whose behavior is determined by the type of its first operand.

	After a successful call to check(), this class acts as a proxy to the class
	of the deduced effective operator.

	Subclasses must provide:
	- `morph_table`: dictionary. Maps types to type-specific operator classes.
	  See check().
	- `_lhs_type_error`: method called when LHS's type is absent from
	  `morph_table`.
	"""

	def check(self, context, logger, mode='r'):
		"""
		Check LHS, determine the operator's behavior from LHS's type, and
		create the adequate type-specific operator.
		After this method succeeds, the BinaryPolymorphicOp object acts as a
		proxy to the type-specific operator object.
		"""
		# Guilty until proven innocent
		self.resolved_type = types.ERRONEOUS
		self.lhs.check(context, logger, mode)
		if isinstance(self.lhs.resolved_type, types.Scalar):
			key = self.lhs.resolved_type
		else:
			key = type(self.lhs.resolved_type)
		try:
			morph_cls = self.morph_table[key]
		except (TypeError, KeyError):
			self._lhs_type_error(logger)
		else:
			self._morph = morph_cls(self.pos, self.lhs, self.rhs)
			# From now on, we're nothing more than a proxy to self._morph.
			self.check_rhs(context, logger)

	def __getattribute__(self, name):
		try:
			morph = object.__getattribute__(self, '_morph')
		except AttributeError:
			return object.__getattribute__(self, name)
		try:
			return getattr(morph, name)
		except AttributeError:
			return object.__getattribute__(self, name)

	def _lhs_type_error(self, logger):
		raise NotImplementedError

class NumberArithmeticOp(BinaryChameleonOp):
	@nonwritable
	def check(self, context, logger):
		super().check(context, logger)
		if self.resolved_type not in (types.INTEGER, types.REAL):
			logger.log(semantic.TypeError(self.pos,
					"cet opérateur ne peut être appliqué qu'à des nombres",
					self.resolved_type))

class BinaryComparisonOp(BinaryOp):
	"""
	Binary operator of boolean type, taking operands of equivalent types.
	"""
	resolved_type = types.BOOLEAN

	@nonwritable
	def check(self, context, logger):
		self.lhs.check(context, logger)
		self.rhs.check(context, logger)
		ltype, rtype = self.lhs.resolved_type, self.rhs.resolved_type
		strongtype = ltype.equivalent(rtype)
		if strongtype is None:
			logger.log(semantic.TypeMismatch(self.pos, "les types des opérandes "
					"doivent être équivalents",
					ltype, rtype))

class BinaryLogicalOp(BinaryOp):
	"""
	Binary operator of boolean type, taking operands of boolean types.
	"""
	resolved_type = types.BOOLEAN

	@nonwritable
	def check(self, context, logger):
		for side in (self.lhs, self.rhs):
			side.check(context, logger)
			semantictools.enforce("cet opérande", types.BOOLEAN, side, logger)


#######################################################################
#
# UNARY OPERATORS
#
#######################################################################

class UnaryPlus(UnaryNumberOp):
	keyword_def = kw.PLUS

	def js(self, pp):
		self.rhs.js(pp)

class UnaryMinus(UnaryNumberOp):
	keyword_def = kw.MINUS
	js_kw = "-"

class LogicalNot(UnaryOp):
	keyword_def = kw.NOT
	resolved_type = types.BOOLEAN
	js_kw = "!"

	@nonwritable
	def check(self, context, logger):
		self.rhs.check(context, logger)
		semantictools.enforce("l'opérande du 'non'", types.BOOLEAN, self.rhs, logger)

#######################################################################
#
# BINARY OPERATORS
#
#######################################################################

class _ArraySubscript(BinaryOp):
	keyword_def = kw.LSBRACK
	closing = kw.RSBRACK

	def check_rhs(self, context, logger):
		# Guilty until proven innocent
		self.resolved_type = types.ERRONEOUS
		array = self.lhs.resolved_type
		# check dimension count
		ldims = len(array.dimensions)
		rdims = len(self.rhs)
		if ldims != rdims:
			logger.log(semantic.DimensionCountMismatch(
				self.pos, given=rdims, expected=ldims))
			return
		# check indices in arglist
		for index in self.rhs:
			index.check(context, logger)
			semantictools.enforce("cet indice de tableau", types.INTEGER, index, logger)
		self.resolved_type = array.resolved_element_type

	def js_indices(self, pp):
		"""
		Generate a JavaScript translation of the array indices.
		"""
		pp.put("[")
		pp.join(self.rhs, pp.put, ",")
		pp.put("]")

	# JS getter
	def js(self, pp):
		pp.put(self.lhs, ".get(")
		self.js_indices(pp)
		pp.put(")")

	# JS setter
	def js_assign_lhs(self, pp, assignment):
		pp.put(self.lhs, ".set(")
		self.js_indices(pp)
		pp.put(", ", assignment.rhs, ")")

	def lda(self, pp):
		pp.put(self.lhs, "[")
		pp.join(self.rhs, pp.put, ", ")
		pp.put("]")


class _StringSubscript(BinaryOp):
	keyword_def = kw.LSBRACK
	closing = kw.RSBRACK

	def check_rhs(self, context, logger):
		# check parameter count
		rdims = len(self.rhs)
		if 1 != rdims:
			logger.log(semantic.ParameterCountMismatch(
				self.pos, given=rdims, expected=1))
			return
		self.index = self.rhs[0]
		self.index.check(context, logger)
		itype = self.index.resolved_type
		if itype is types.INTEGER:
			self.resolved_type = types.CHARACTER
		elif itype is types.RANGE:
			self.resolved_type = types.STRING
		else:
			logger.log(semantic.TypeError(self.index.pos, "les indices de chaînes doivent "
					"être des entiers ou des intervalles", itype))
			self.resolved_type = types.ERRONEOUS

	def js(self, pp):
		if self.resolved_type is types.CHARACTER:
			pp.put(self.lhs, "[", self.index, "]")
		elif self.resolved_type is types.STRING:
			start = self.index.lhs
			end = self.index.rhs
			pp.put(self.lhs, ".substr(", start, ", 1+", end, "-", start, ")")
		else:
			assert False

	def lda(self, pp):
		pp.put(self.lhs, "[", self.index, "]")


class Subscript(BinaryPolymorphicOp):
	"""
	Array subscript operator.

	Encompassing.
	LHS is an array variable identifier.
	RHS is a list of indices, which should resolve to integers.

	Unlike most expressions, this operator is *writable*.
	"""

	keyword_def = kw.LSBRACK
	closing = kw.RSBRACK

	def _lhs_type_error(self, logger):
		logger.log(semantic.NonSubscriptable(self.pos, self.lhs.resolved_type))

	morph_table = {
			types.Array: _ArraySubscript,
			types.STRING: _StringSubscript,
	}


class FunctionCall(BinaryOp):
	"""
	Function call operator.

	Encompassing.
	LHS is a function identifier.
	RHS is an arglist of effective parameters.
	"""

	keyword_def = kw.LPAREN
	closing = kw.RPAREN

	def __init__(self, pos, lhs, rhs):
		# Report position as lhs's position (makes for more understandable
		# errors instead of reporting the opening parenthesis's position)
		super().__init__(lhs.pos, lhs, rhs)

	@nonwritable
	def check(self, context, logger):
		self.lhs.check(context, logger)
		try:
			self.function = self.lhs.bound
			check_call = getattr(self.function, 'check_call')
		except AttributeError:
			logger.log(semantic.NonCallable(self.pos, self.lhs.resolved_type))
			self.resolved_type = types.ERRONEOUS
			return
		check_call(context, logger, self.pos, self.rhs)
		self.resolved_type = self.function.resolved_return_type

	def lda(self, pp):
		pp.put(self.lhs, "(")
		pp.join(self.rhs, pp.put, ", ")
		pp.put(")")

	def js(self, pp):
		self.function.js_call(pp, self.rhs)

class MemberSelect(BinaryOp):
	"""
	Composite member selection operator.
	
	LHS's typedef resolves to a "pure" composite
	(i.e. not an array of composites).
	RHS resolves to a valid member of the composite.

	Unlike most expressions, this operator is *writable*.
	"""

	keyword_def = kw.DOT

	def check(self, context, logger, mode='r'):
		# LHS is supposed to refer to a TypeAlias, which refers to a composite
		self.lhs.check(context, logger)
		composite = self.lhs.resolved_type
		if not isinstance(composite, types.Composite):
			logger.log(semantic.NonComposite(self.pos, composite))
			self.resolved_type = types.ERRONEOUS
		else:
			# use composite context exclusively for RHS
			self.rhs.check(composite.context, logger, mode)
			self.resolved_type = self.rhs.resolved_type

	def lda(self, pp):
		pp.put(self.lhs, self.keyword_def, self.rhs)
	
	def js(self, pp):
		pp.put(self.lhs, ".", self.rhs)

class Power(NumberArithmeticOp):
	"""
	Exponent.

	Right-associative.
	The typedef of both operands must resolve to a number.
	"""

	keyword_def = kw.POWER
	right_ass = True

	def js(self, pp):
		pp.put("Math.pow(", self.lhs, ", ", self.rhs, ")")

class Multiplication(NumberArithmeticOp):
	keyword_def = kw.TIMES
	js_kw = "*"

class RealDivision(BinaryOp):
	keyword_def = kw.SLASH
	js_kw = "/"
	resolved_type = types.REAL

	@nonwritable
	def check(self, context, logger):
		for side in (self.lhs, self.rhs):
			side.check(context, logger)
			semantictools.enforce_compatible("les opérandes d'une division réelle",
					types.REAL, self.lhs, logger)

class IntegerDivision(BinaryOp):
	keyword_def = kw.COLON
	resolved_type = types.INTEGER

	@nonwritable
	def check(self, context, logger):
		for side in (self.lhs, self.rhs):
			side.check(context, logger)
			semantictools.enforce_compatible("les opérandes d'une division entière",
					types.INTEGER, self.lhs, logger)

	def js(self, pp):
		pp.put("Math.floor((", self.lhs, "/", self.rhs, "))")

class Modulo(NumberArithmeticOp):
	keyword_def = kw.MODULO
	js_kw = "%"

class _Addition(BinaryOp):
	keyword_def = kw.PLUS
	js_kw = "+"

	def check_rhs(self, context, logger):
		self.rhs.check(context, logger)
		ltype, rtype = self.lhs.resolved_type, self.rhs.resolved_type
		strongest = ltype.equivalent(rtype)
		if strongest not in (types.INTEGER, types.REAL):
			logger.log(semantic.TypeMismatch(self.pos, "les types des opérandes "
					"doivent être équivalents", ltype, rtype))
			self.resolved_type = types.ERRONEOUS
		else:
			self.resolved_type = strongest

class _Concatenation(BinaryOp):
	keyword_def = kw.PLUS
	js_kw = "+"
	resolved_type = types.STRING

	def check_rhs(self, context, logger):
		self.rhs.check(context, logger)
		ltype, rtype = self.lhs.resolved_type, self.rhs.resolved_type
		strongest = ltype.equivalent(rtype)
		if strongest not in (types.STRING, types.CHARACTER):
			logger.log(semantic.TypeMismatch(self.pos, "les types des opérandes "
					"doivent être équivalents", ltype, rtype))
			self.resolved_type = types.ERRONEOUS

class Plus(BinaryPolymorphicOp):
	"""
	Polymorphic operator
	- Number operands: addition
	- String/character operands: string concatenation

	Minimalist implementation because JavaScript's '+' operator happens to have
	exactly the same behavior (in the restricted use cases that are allowed by
	check() anyway).
	"""

	keyword_def = kw.PLUS
	js_kw = "+" # Warning: this works because the JS plus has exactly the same behavior

	def _lhs_type_error(self, logger):
		logger.log(semantic.TypeError(self.pos, "l'opérateur + ne fonctionne qu'avec des "
				"nombres ou des chaînes/caractères", self.lhs.resolved_type))

	morph_table = {
			types.STRING:    _Concatenation,
			types.CHARACTER: _Concatenation,
			types.INTEGER:   _Addition,
			types.REAL:      _Addition,
	}

class Subtraction(NumberArithmeticOp):
	keyword_def = kw.MINUS
	js_kw = "-"

class IntegerRange(BinaryOp):
	keyword_def = kw.DOTDOT
	resolved_type = types.RANGE

	@nonwritable
	def check(self, context, logger):
		for operand in (self.lhs, self.rhs):
			operand.check(context, logger)
			semantictools.enforce("une borne d'intervalle", types.INTEGER, operand, logger)

	def js(self, pp):
		raise NotImplementedError

class LessThan(BinaryComparisonOp):
	keyword_def = kw.LT
	js_kw = "<"

class GreaterThan(BinaryComparisonOp):
	keyword_def = kw.GT
	js_kw = ">"

class LessOrEqual(BinaryComparisonOp):
	keyword_def = kw.LE
	js_kw = "<="

class GreaterOrEqual(BinaryComparisonOp):
	keyword_def = kw.GE
	js_kw = ">="

class Equal(BinaryComparisonOp):
	keyword_def = kw.EQ
	js_kw = "==="

class NotEqual(BinaryComparisonOp):
	keyword_def = kw.NE
	js_kw = "!=="

class LogicalAnd(BinaryLogicalOp):
	keyword_def = kw.AND
	js_kw = "&&"

class LogicalOr(BinaryLogicalOp):
	keyword_def = kw.OR
	js_kw = "||"


#######################################################################
#
# LISTS OF OPERATORS, BINARY OPERATOR PRECEDENCES, ASSERTIONS
#
#######################################################################

unary = [
		UnaryPlus,
		UnaryMinus,
		LogicalNot
]

binary_precedence = [
		[Subscript, FunctionCall, MemberSelect],
		[Power],
		[Multiplication, RealDivision, IntegerDivision, Modulo],
		[Plus, Subtraction],
		[IntegerRange],
		[LessThan, GreaterThan, LessOrEqual, GreaterOrEqual],
		[Equal, NotEqual],
		[LogicalAnd],
		[LogicalOr],
]

binary_flat = [opcls for sublist in binary_precedence for opcls in sublist]

unary_keyword_defs = [opcls.keyword_def for opcls in unary]
binary_keyword_defs = [opcls.keyword_def for opcls in binary_flat]

for cls in unary:
	assert(issubclass(cls, UnaryOp))

for i, group in enumerate(binary_precedence):
	group_id = len(binary_precedence) - i - 1
	for cls in group:
		assert(issubclass(cls, BinaryOp))
		cls.precedence = group_id

