from . import keywords as kw
from .expression import Expression
from .errors import semantic
from . import typedesc
from . import module
from . import dot

#######################################################################
#
# BASE OPERATOR CLASSES
#
#######################################################################

class UnaryOp(Expression):
	right_ass = True

	def __init__(self, pos, rhs=None):
		super().__init__(pos)
		self.rhs = rhs

	def put_node(self, cluster):
		op_node = dot.Node(self.keyword_def.default_spelling,
				cluster, self.rhs.put_node(cluster))
		op_node.shape = "circle"
		return op_node
		
	def lda_format(self, indent=0):
		return indent*'\t' + self.rhs

	def check(self, context):
		raise NotImplementedError

class BinaryOp(Expression):
	right_ass = False
	encompass_varargs_till = None

	def __init__(self, pos, lhs=None, rhs=None):
		super().__init__(pos)
		self.lhs = lhs
		self.rhs = rhs

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

	def lda_format(self, indent=0):
		if self.encompass_varargs_till is None:
			after_lhs = " {} ".format(self.keyword_def)
			after_rhs = ""
		else:
			after_lhs = str(self.keyword_def)
			after_rhs = str(self.encompass_varargs_till)
		return "{lhs}{after_lhs}{rhs}{after_rhs}".format(
				lhs = self.lhs.lda_format(),
				rhs = self.rhs.lda_format(),
				after_lhs = after_lhs,
				after_rhs = after_rhs)

	def check(self, context):
		raise NotImplementedError

class BinaryOpEquivalentSides(BinaryOp):
	def check(self, context):
		# TODO types "équivalents" (réels ~ entiers)
		lhs_typedef = self.lhs.check(context)
		rhs_typedef = self.rhs.check(context)
		if not lhs_typedef.equivalent(rhs_typedef): # TODO!!!!!
			raise semantic.TypeMismatch(self.pos, lhs_typedef, rhs_typedef)
		# TODO avec les types équivalents, il ne faut pas forcément se contenter
		# du type du LHS, mais plutôt du type le plus "fort" (genre réel >
		# entier) - TODO voir avec max()
		if self._take_on_typedef:
			return lhs_typedef
		else:
			return self._typedef

class ArithmeticOp(BinaryOpEquivalentSides):
	_take_on_typedef = True

class BinaryBooleanOp(BinaryOpEquivalentSides):
	_typedef = typedesc.Boolean
	_take_on_typedef = False

ComparisonOp = BinaryBooleanOp

BinaryLogicalOp = BinaryBooleanOp

#######################################################################
#
# UNARY OPERATORS
#
#######################################################################

class _UnaryNumberSign(UnaryOp):
	def check(self, context):
		rhs_typedef = self.rhs.check(context)
		if rhs_typedef not in (typedesc.Integer, typedesc.Real):
			# TODO peut-être que SpecificTypeExpected est plus adapté ici ?
			raise semantic.SemanticError(self.pos, "cet opérateur unaire "
					"ne peut être appliqué qu'à un nombre entier ou réel")
		return rhs_typedef

class UnaryPlus(_UnaryNumberSign):
	keyword_def = kw.PLUS

class UnaryMinus(_UnaryNumberSign):
	keyword_def = kw.MINUS

class LogicalNot(UnaryOp):
	keyword_def = kw.NOT

#######################################################################
#
# BINARY OPERATORS
#
#######################################################################

class ArraySubscript(BinaryOp):
	"""
	Array subscript operator.

	Encompassing.
	LHS resolves to array variable.
	RHS is a Varargs object containing the indices, which should resolve to
	integers.
	"""

	keyword_def = kw.LSBRACK
	encompass_varargs_till = kw.RSBRACK

	def check(self, context):
		array_type = self.lhs.check(context)
		if not isinstance(array_type, typedesc.ArrayType):
			raise semantic.NonSubscriptable(self.pos)
		# check dimension count
		ldims = len(array_type.dimensions)
		rdims = len(self.rhs)
		if ldims != rdims:
			raise semantic.DimensionCountMismatch(self.pos, given=rdims, expected=ldims)
		# check index varargs
		index_types = self.rhs.check(context)
		for type_, item in zip(index_types, self.rhs):
			if type_ is not typedesc.Integer:
				raise semantic.SpecificTypeExpected(item.pos,
						"cet indice de tableau",
						expected=typedesc.Integer, given=type_)
		return array.resolved_element_type

class FunctionCall(BinaryOp):
	"""
	Function call operator.

	Encompassing.
	LHS resolves to function identifier.
	RHS resolves to Varargs object containing the function's effective
	parameters.
	"""

	keyword_def = kw.LPAREN
	encompass_varargs_till = kw.RPAREN

	def check(self, context):
		function = self.lhs.check(context)
		if not isinstance(function, module.Function):
			raise semantic.NonCallable(self.pos)
		# check parameter count
		expected_argc = len(function.fp_list)
		given_argc = len(self.rhs)
		if expected_argc != given_argc:
			raise semantic.ParameterCountMismatch(self.pos,
					given=given_argc, expected=expected_argc)
		# TODO: check parameter types
		raise NotImplementedError("PARAMETER TYPES!!!")
		# TODO: chaque fonction doit avoir un mini-lexique PRÉ-REMPLI de ses paramètres
		return function.return_type
		

class MemberSelect(BinaryOp):
	"""
	Composite member selection operator.
	
	LHS's typedef resolves to a "pure" composite
	(i.e. not an array of composites).
	RHS resolves to a valid member of the composite.
	"""

	keyword_def = kw.DOT

	def check(self, context):
		# LHS is supposed to refer to a composite
		composite = self.lhs.check(context)
		if not isinstance(composite, typedesc.CompositeType):
			raise semantic.NonComposite(self.pos)
		# use composite context exclusively for RHS
		return self.rhs.check(composite.context)

class Power(ArithmeticOp):
	"""
	Exponent.

	Right-associative.
	The typedef of both operands must resolve to a number.
	"""

	keyword_def = kw.POWER
	right_ass = True

class Multiplication(ArithmeticOp):
	keyword_def = kw.TIMES

class Division(ArithmeticOp):
	keyword_def = kw.SLASH

class Modulo(ArithmeticOp):
	keyword_def = kw.MODULO

class Addition(ArithmeticOp):
	keyword_def = kw.PLUS

class Subtraction(ArithmeticOp):
	keyword_def = kw.MINUS

class IntegerRange(BinaryOp):
	keyword_def = kw.DOTDOT
	def check(self, context):
		lhs_typedef = self.lhs.check(context)
		rhs_typedef = self.rhs.check(context)
		for operand in (self.lhs, self.rhs):
			operand_type = operand.check(context)
			if operand_type is not typedesc.Integer:
				raise semantic.SpecificTypeExpected(operand.pos,
						"une borne d'intervalle",
						expected=typedesc.Integer, given=operand_type)
		return typedesc.Range

class LessThan(ComparisonOp):
	keyword_def = kw.LT

class GreaterThan(ComparisonOp):
	keyword_def = kw.GT

class LessOrEqual(ComparisonOp):
	keyword_def = kw.LE

class GreaterOrEqual(ComparisonOp):
	keyword_def = kw.GE

class Equal(ComparisonOp):
	keyword_def = kw.EQ

class NotEqual(ComparisonOp):
	keyword_def = kw.NE

class LogicalAnd(BinaryLogicalOp):
	keyword_def = kw.AND

class LogicalOr(BinaryLogicalOp):
	keyword_def = kw.OR

class Assignment(BinaryOpEquivalentSides):
	keyword_def = kw.ASSIGN
	right_ass = True
	# an assignment cannot be part of another expression,
	# therefore its type always resolves to None
	_typedef = None
	_take_on_typedef = False

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

