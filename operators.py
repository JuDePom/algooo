import keywords as kw
import typedef
from expression import Expression
from errors import *
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
		self.lhs.check(context)
		self.rhs.check(context)
		if self.lhs.typedef != self.rhs.typedef:
			raise TypeMismatch(self.pos, self.lhs.typedef, self.rhs.typedef)
		# TODO avec les types équivalents, il ne faut pas forcément se contenter
		# du type du LHS, mais plutôt du type le plus "fort" (genre réel >
		# entier) - TODO voir avec max()
		if self.take_on_typedef:
			self.typedef = self.lhs.typedef

#######################################################################
#
# UNARY OPERATORS
#
#######################################################################

class _UnaryNumberSign(UnaryOp):
	def check(self, context):
		self.rhs.check(context)
		if self.rhs.typedef not in (kw.INT, kw.REAL):
			print(self.rhs.typedef)
			raise LDASemanticError(self.pos, "cet opérateur unaire "
					"ne peut être appliqué qu'à un nombre entier ou réel")
		self.typedef = self.rhs.typedef

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
		self.lhs.check(context)
		if not self.lhs.typedef.array:
			raise LDASemanticError(self.pos,
					"l'élément indexé n'est pas un tableau")
		# check if the dimension count in RHS matches LHS's typedef
		ldims = len(self.lhs.typedef.array_dimensions)
		rdims = len(self.rhs)
		if ldims != rdims:
			raise LDASemanticError(self.pos, "le nombre d'indices ne "
					"correspond pas au nombre de dimensions du tableau")
		# check index varargs
		self.rhs.check(context)
		for arg in self.rhs:
			if arg.typedef != kw.INT:
				raise LDASemanticError(self.pos,
						"tous les indices doivent être des entiers")
		self.typedef = self.lhs.typedef.make_pure()

class FunctionCall(BinaryOp):
	"""
	Function call operator.

	Encompassing.
	LHS resolves to function identifier.
	RHS resolves to Varargs object containing the function's effective
	parameters.
	"""

	keyword_def = kw.LPAREN

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
		self.lhs.check(context)
		if not self.lhs.typedef.pure_composite:
			raise LDASemanticError(self.pos, "sélection d'un membre "
				"dans un élément de type non-composite")
		# TODO very ugly
		composite = context.composites[self.lhs.typedef.composite_name]
		# use composite context exclusively for RHS
		self.rhs.check(composite)
		self.typedef = self.rhs.typedef

class Power(BinaryOp):
	"""
	Exponent.

	Right-associative.
	The typedef of both operands must resolve to a number.
	"""

	keyword_def = kw.POWER
	right_ass = True

class Multiplication(BinaryOpEquivalentSides):
	keyword_def = kw.TIMES
	take_on_typedef = True

class Division(BinaryOpEquivalentSides):
	keyword_def = kw.SLASH
	take_on_typedef = True

class Modulo(BinaryOpEquivalentSides):
	keyword_def = kw.MODULO
	take_on_typedef = True

class Addition(BinaryOpEquivalentSides):
	keyword_def = kw.PLUS
	take_on_typedef = True

class Subtraction(BinaryOpEquivalentSides):
	keyword_def = kw.MINUS
	take_on_typedef = True

class IntegerRange(BinaryOp):
	keyword_def = kw.DOTDOT

class LessThan(BinaryOpEquivalentSides):
	keyword_def = kw.LT
	typedef = typedef.BOOL
	take_on_typedef = False

class GreaterThan(BinaryOpEquivalentSides):
	keyword_def = kw.GT
	typedef = typedef.BOOL
	take_on_typedef = False

class LessOrEqual(BinaryOpEquivalentSides):
	keyword_def = kw.LE
	typedef = typedef.BOOL
	take_on_typedef = False

class GreaterOrEqual(BinaryOpEquivalentSides):
	keyword_def = kw.GE
	typedef = typedef.BOOL
	take_on_typedef = False

class Equal(BinaryOpEquivalentSides):
	keyword_def = kw.EQ
	typedef = typedef.BOOL
	take_on_typedef = False

class NotEqual(BinaryOpEquivalentSides):
	keyword_def = kw.NE
	typedef = typedef.BOOL
	take_on_typedef = False

class LogicalAnd(BinaryOpEquivalentSides):
	keyword_def = kw.AND
	typedef = typedef.BOOL
	take_on_typedef = False

class LogicalOr(BinaryOpEquivalentSides):
	keyword_def = kw.OR
	typedef = typedef.BOOL
	take_on_typedef = False

class Assignment(BinaryOpEquivalentSides):
	keyword_def = kw.ASSIGN
	right_ass = True
	# an assignment cannot be part of another expression,
	# therefore its type always resolves to None
	typedef = None
	take_on_typedef = False

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

