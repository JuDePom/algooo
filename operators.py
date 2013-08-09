import keywords as kw
from expression import Expression
from errors import *
from symboltable import scalars
from symboltable import Identifier
import dot

#######################################################################
#
# BASE OPERATOR CLASSES & SEMANTIC CHECKS
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

	def check(self, context):
		raise NotImplementedError

class BinaryOpEquivalentSides(BinaryOp):
	def check(self, context):
		# TODO types "équivalents" (réels ~ entiers)
		lhs_typedef = self.lhs.check(context)
		rhs_typedef = self.rhs.check(context)
		if not lhs_typedef.equivalent(rhs_typedef): # TODO!!!!!
			raise TypeMismatch(self.pos, lhs_typedef, rhs_typedef)
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
	_typedef = scalars['BOOL']
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
		if rhs_typedef not in (scalars['INT'], scalars['REAL']):
			raise LDASemanticError(self.pos, "cet opérateur unaire "
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
		lhs_typedef = self.lhs.check(context)
		if not lhs_typedef.array:
			raise LDASemanticError(self.pos,
					"l'élément indexé n'est pas un tableau")
		# check if the dimension count in RHS matches LHS's typedef
		ldims = len(lhs_typedef.array_dimensions)
		rdims = len(self.rhs)
		if ldims != rdims:
			raise LDASemanticError(self.pos, "le nombre d'indices ne "
					"correspond pas au nombre de dimensions du tableau")
		# check index varargs
		arg_typedefs = self.rhs.check(context)
		for typedef in arg_typedefs:
			if typedef != scalars['INT']:
				raise LDASemanticError(self.pos,
						"tous les indices doivent être des entiers")
		return lhs_typedef.make_pure()

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
		bound_function = self.lhs.check(context)
		if not isinstance(bound_function, Function):
			raise LDASemanticError("cet élément ne peut pas être appelé car "
					"ce n'est pas une fonction")
		# TODO check varargs
		return bound_function.return_type
		

class MemberSelect(BinaryOp):
	"""
	Composite member selection operator.
	
	LHS's typedef resolves to a "pure" composite
	(i.e. not an array of composites).
	RHS resolves to a valid member of the composite.
	"""

	keyword_def = kw.DOT

	def check(self, context):
		# LHS's typedef should resolve to composite
		lhs_typedef = self.lhs.check(context)
		if not lhs_typedef.pure_composite:
			raise LDASemanticError(self.pos, "sélection d'un membre "
				"dans un élément de type non-composite")
		composite = context.composites[lhs_typedef.composite_name]
		# use composite context exclusively for RHS
		return self.rhs.check(composite)

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

