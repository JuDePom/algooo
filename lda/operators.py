from .expression import Expression, surround
from .errors import semantic
from . import types
from . import dot
from . import kw

#######################################################################
#
# GENERIC OPERATOR BASE CLASSES
#
#######################################################################

class UnaryOp(Expression):
	right_ass = True

	def __init__(self, pos, rhs=None):
		super().__init__(pos)
		self.rhs = rhs

	def __eq__(self, other):
		return type(self) == type(other) and self.rhs == other.rhs

	def put_node(self, cluster):
		op_node = dot.Node(self.keyword_def.default_spelling,
				cluster, self.rhs.put_node(cluster))
		op_node.shape = "circle"
		return op_node
		
	@surround
	def lda(self, pp):
		pp.put(self.keyword_def, " ", self.rhs)
		
	@surround
	def js(self, pp):
		pp.put(self.js_kw, " ", self.rhs)

	def check(self, context, logger):
		raise NotImplementedError

class BinaryOp(Expression):
	right_ass = False

	def __init__(self, pos, lhs=None, rhs=None):
		super().__init__(pos)
		self.lhs = lhs
		self.rhs = rhs

	def __eq__(self, other):
		return type(self) == type(other) and \
				self.lhs == other.lhs and \
				self.rhs == other.rhs

	def part_of_rhs(self, whose):
		return self.precedence > whose.precedence or \
			(self.right_ass and self.precedence == whose.precedence)

	def put_node(self, cluster):
		op_node = dot.Node(self.keyword_def.default_spelling,
				cluster,
				self.lhs.put_node(cluster),
				self.rhs.put_node(cluster))
		op_node.shape = "circle"
		return op_node

	@surround
	def lda(self, pp):
		pp.put(self.lhs, " ", self.keyword_def, " ", self.rhs)
	
	@surround
	def js(self, pp):
		pp.put(self.lhs, " ", self.js_kw, " ", self.rhs)

	def check(self, context, logger):
		raise NotImplementedError

#######################################################################
#
# SPECIFIC OPERATOR BASE CLASSES
#
#######################################################################

class UnaryNumberOp(UnaryOp):
	"""
	Unary operator that can only be used with a number type.
	"""
	def check(self, context, logger):
		self.rhs.check(context, logger)
		rtype = self.rhs.resolved_type
		if rtype not in (types.INTEGER, types.REAL):
			# TODO peut-être que SpecificTypeExpected est plus adapté ici ?
			logger.log(semantic.SemanticError(self.pos, "cet opérateur unaire "
					"ne peut être appliqué qu'à un nombre entier ou réel"))
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

class NumberArithmeticOp(BinaryChameleonOp):
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

	def check(self, context, logger):
		for side in (self.lhs, self.rhs):
			side.check(context, logger)
			types.enforce("cet opérande", types.BOOLEAN, side, logger)

class BinaryEncompassingOp(BinaryOp):
	"""
	Binary operator whose righthand operand is a list of comma-separated
	arguments. The last argument is followed by a closing keyword, therefore
	subclasses *must* define the `closing` member.
	"""

	closing = None # must be defined by subclasses!

	def lda(self, pp):
		pp.put(self.lhs, self.keyword_def)
		pp.join(self.rhs, pp.put, kw.COMMA, " ")
		pp.put(self.closing)


#######################################################################
#
# UNARY OPERATORS
#
#######################################################################

class UnaryPlus(UnaryNumberOp):
	keyword_def = kw.PLUS

class UnaryMinus(UnaryNumberOp):
	keyword_def = kw.MINUS

class LogicalNot(UnaryOp):
	keyword_def = kw.NOT

#######################################################################
#
# BINARY OPERATORS
#
#######################################################################

class ArraySubscript(BinaryEncompassingOp):
	"""
	Array subscript operator.

	Encompassing.
	LHS is an array variable identifier.
	RHS is an arglist of indices, which should resolve to integers.

	Unlike most expressions, this operator is *writable*.
	"""

	writable = True
	keyword_def = kw.LSBRACK
	closing = kw.RSBRACK

	def check(self, context, logger):
		# guilty until proven innocent
		self.resolved_type = types.ERRONEOUS
		# are we trying to subscript an array?
		self.lhs.check(context, logger)
		array = self.lhs.resolved_type
		if not isinstance(array, types.Array):
			logger.log(semantic.NonSubscriptable(self.pos, array))
			return
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
			types.enforce("cet indice de tableau", types.INTEGER, index, logger)
		self.resolved_type = array.element_type.resolved_type

class FunctionCall(BinaryEncompassingOp):
	"""
	Function call operator.

	Encompassing.
	LHS is a function identifier.
	RHS is an arglist of effective parameters.
	"""

	keyword_def = kw.LPAREN
	closing = kw.RPAREN

	def check(self, context, logger):
		self.resolved_type = types.ERRONEOUS # guilty until proven innocent
		self.lhs.check(context, logger)
		self.function = self.lhs.resolved_type
		for effective in self.rhs:
			effective.check(context, logger)
		try:
			self.function.check_effective_parameters(context, logger, self.pos, self.rhs)
			self.resolved_type = self.function.return_type.resolved_type
		except AttributeError:
			logger.log(semantic.NonCallable(self.pos, self.function.resolved_type))
			return

	def js(self, pp):
		self.function.js_call(pp, self)

class MemberSelect(BinaryOp):
	"""
	Composite member selection operator.
	
	LHS's typedef resolves to a "pure" composite
	(i.e. not an array of composites).
	RHS resolves to a valid member of the composite.

	Unlike most expressions, this operator is *writable*.
	"""

	writable = True
	keyword_def = kw.DOT

	def check(self, context, logger):
		# LHS is supposed to refer to a TypeAlias, which refers to a composite
		self.lhs.check(context, logger)
		composite = self.lhs.resolved_type
		if not isinstance(composite, types.Composite):
			logger.log(semantic.NonComposite(self.pos, composite))
			self.resolved_type = types.ERRONEOUS
		else:
			# use composite context exclusively for RHS
			self.rhs.check(composite.context, logger)
			self.resolved_type = self.rhs.resolved_type

	@surround
	def lda(self, pp):
		pp.put(self.lhs, self.keyword_def, self.rhs)
	
	@surround
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

class Division(NumberArithmeticOp):
	keyword_def = kw.SLASH
	js_kw = "/"
	#TODO: JS integer division!!!

class Modulo(NumberArithmeticOp):
	keyword_def = kw.MODULO
	js_kw = "%"

class Addition(NumberArithmeticOp):
	keyword_def = kw.PLUS
	js_kw = "+"

class Subtraction(NumberArithmeticOp):
	keyword_def = kw.MINUS
	js_kw = "-"

class IntegerRange(BinaryOp):
	keyword_def = kw.DOTDOT
	resolved_type = types.RANGE

	def check(self, context, logger):
		for operand in (self.lhs, self.rhs):
			operand.check(context, logger)
			types.enforce("une borne d'intervalle", types.INTEGER, operand, logger)

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
		[ArraySubscript, FunctionCall, MemberSelect],
		[Power],
		[Multiplication, Division, Modulo],
		[Addition, Subtraction],
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

