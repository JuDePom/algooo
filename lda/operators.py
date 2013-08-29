from .expression import Expression
from .errors import semantic
from . import types
from . import module
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
		
	def lda(self, exp):
		exp.put(self.keyword_def, " ", self.rhs)
		
	def js(self, exp):
		exp.put(self.keyword_def, " ", self.rhs)

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

	def lda(self, exp):
		exp.put(self.lhs, " ", self.keyword_def, " ", self.rhs)
	
	def js(self, exp):
		# TODO this is obviously very wrong
		exp.put(self.lhs, " ", self.keyword_def, " ", self.rhs)

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

	def lda(self, exp):
		exp.put(self.keyword_def, self.rhs)
	
	def js(self, exp):
		exp.put(self.keyword_def, self.rhs)

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

	def lda(self, exp):
		exp.put(self.lhs, self.keyword_def, self.rhs, self.closing)

	def js(self, exp):
		# TODO this is obviously very wrong
		exp.put(self.lhs, self.keyword_def, self.rhs, self.closing)


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
	"""

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
		# guilty until proven innocent
		self.resolved_type = types.ERRONEOUS
		# are we trying to call a function?
		self.lhs.check(context, logger)
		function = self.lhs.resolved_type
		if not isinstance(function, module.Function):
			logger.log(semantic.NonCallable(self.pos, function.resolved_type))
			return
		# check parameter count
		expected_argc = len(function.fp_list)
		given_argc = len(self.rhs)
		if expected_argc != given_argc:
			logger.log(semantic.ParameterCountMismatch(self.pos,
					given=given_argc, expected=expected_argc))
			return
		# check parameter types
		for effective, formal in zip(self.rhs, function.fp_list):
			effective.check(context, logger)
			types.enforce_compatible("ce paramètre effectif",
					formal.resolved_type, effective, logger)
		self.resolved_type = function.return_type.resolved_type

class MemberSelect(BinaryOp):
	"""
	Composite member selection operator.
	
	LHS's typedef resolves to a "pure" composite
	(i.e. not an array of composites).
	RHS resolves to a valid member of the composite.
	"""

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

	def lda(self, exp):
		exp.put(self.lhs, self.keyword_def, self.rhs)
	
	def js(self, exp):
		exp.put(self.lhs, self.keyword_def, self.rhs)

class Power(BinaryChameleonOp):
	"""
	Exponent.

	Right-associative.
	The typedef of both operands must resolve to a number.
	"""

	keyword_def = kw.POWER
	right_ass = True

class Multiplication(BinaryChameleonOp):
	keyword_def = kw.TIMES

class Division(BinaryChameleonOp):
	keyword_def = kw.SLASH

class Modulo(BinaryChameleonOp):
	keyword_def = kw.MODULO

class Addition(BinaryChameleonOp):
	keyword_def = kw.PLUS

class Subtraction(BinaryChameleonOp):
	keyword_def = kw.MINUS

class IntegerRange(BinaryOp):
	keyword_def = kw.DOTDOT
	resolved_type = types.RANGE

	def check(self, context, logger):
		for operand in (self.lhs, self.rhs):
			operand.check(context, logger)
			types.enforce("une borne d'intervalle", types.INTEGER, operand, logger)

class LessThan(BinaryComparisonOp):
	keyword_def = kw.LT
	
	def js(self, exp):
		exp.put( self.lhs, " < ", self.rhs)

class GreaterThan(BinaryComparisonOp):
	keyword_def = kw.GT
	
	def js(self, exp):
		exp.put( self.lhs, " > ", self.rhs)

class LessOrEqual(BinaryComparisonOp):
	keyword_def = kw.LE
	
	def js(self, exp):
		exp.put( self.lhs, " <= ", self.rhs)

class GreaterOrEqual(BinaryComparisonOp):
	keyword_def = kw.GE
	
	def js(self, exp):
		exp.put( self.lhs, " >= ", self.rhs)

class Equal(BinaryComparisonOp):
	keyword_def = kw.EQ
	
	def js(self, exp):
		exp.put( self.lhs, " == ", self.rhs)

class NotEqual(BinaryComparisonOp):
	keyword_def = kw.NE

	def js(self, exp):
		exp.put( self.lhs, " != ", self.rhs)
		
class LogicalAnd(BinaryLogicalOp):
	keyword_def = kw.AND
	
	def js(self, exp):
		exp.put( self.lhs, " && ", self.rhs)

class LogicalOr(BinaryLogicalOp):
	keyword_def = kw.OR
	
	def js(self, exp):
		exp.put( self.lhs, " || ", self.rhs)

class Assignment(BinaryOp):
	keyword_def = kw.ASSIGN
	right_ass = True
	# an assignment cannot be part of another expression, therefore it has no type
	resolved_type = types.ASSIGNMENT

	def check(self, context, logger):
		self.lhs.check(context, logger)
		self.rhs.check(context, logger)
		ltype = self.lhs.resolved_type
		rtype = self.rhs.resolved_type
		if not ltype.compatible(rtype):
			logger.log(semantic.TypeMismatch(self.rhs.pos, "le type de l'opérande de "
					"droite doit être compatible avec le type de l'opérande de gauche",
					ltype, rtype))

	def js(self, exp):
		exp.put( self.lhs, " = ", self.rhs)

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
		[Assignment]
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

