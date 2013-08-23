from . import keywords as kw
from .expression import Expression
from .errors import semantic
from . import typedesc
from . import module
from . import dot

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

#######################################################################
#
# SPECIFIC OPERATOR BASE CLASSES
#
#######################################################################

class UnaryNumberOp(UnaryOp):
	"""
	Unary operator that can only be used with a number type.
	"""
	def check(self, context):
		rtype = self.rhs.check(context).resolved_type
		if rtype not in (typedesc.Integer, typedesc.Real):
			# TODO peut-être que SpecificTypeExpected est plus adapté ici ?
			raise semantic.SemanticError(self.pos, "cet opérateur unaire "
					"ne peut être appliqué qu'à un nombre entier ou réel")
		self.resolved_type = rtype
		return self

class BinaryChameleonOp(BinaryOp):
	"""
	Binary operator taking operands of equivalent types. The type of the operator
	is determined by the strongest type among the operands.
	"""
	def check(self, context):
		ltype = self.lhs.check(context).resolved_type
		rtype = self.rhs.check(context).resolved_type
		strongtype = ltype.equivalent(rtype)
		if strongtype is None:
			raise semantic.TypeMismatch(self.pos, "les types des opérandes doivent "
					"être équivalents", ltype, rtype)
		self.resolved_type = strongtype
		return self

class BinaryComparisonOp(BinaryOp):
	"""
	Binary operator of boolean type, taking operands of equivalent types.
	"""
	resolved_type = typedesc.Boolean

	def check(self, context):
		ltype = self.lhs.check(context).resolved_type
		rtype = self.rhs.check(context).resolved_type
		strongtype = ltype.equivalent(rtype)
		if strongtype is None:
			raise semantic.TypeMismatch(self.pos, "les types des opérandes doivent "
					"être équivalents", ltype, rtype)
		return self

class BinaryLogicalOp(BinaryOp):
	"""
	Binary operator of boolean type, taking operands of boolean types.
	"""
	resolved_type = typedesc.Boolean

	def check(self, context):
		for side in (self.lhs, self.rhs):
			sidetype = side.check(context).resolved_type
			if sidetype is not typedesc.Boolean:
				raise semantic.SpecificTypeExpected(side.pos, "cet opérande",
						expected=typedesc.Boolean, given=sidetype)
		return self

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
		array_type = self.lhs.check(context).resolved_type
		if not isinstance(array_type, typedesc.ArrayType):
			raise semantic.NonSubscriptable(self.pos)
		# check dimension count
		ldims = len(array_type.dimensions)
		rdims = len(self.rhs)
		if ldims != rdims:
			raise semantic.DimensionCountMismatch(self.pos, given=rdims, expected=ldims)
		# check index varargs
		indices = self.rhs.check(context)
		for index, item in zip(indices, self.rhs):
			if index.resolved_type is not typedesc.Integer:
				raise semantic.SpecificTypeExpected(item.pos,
						"cet indice de tableau",
						expected=typedesc.Integer, given=index.resolved_type)
		self.resolved_type = array.resolved_element_type
		return self

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
		# check parameter types
		for effective_param, formal_type in zip(self.rhs, function.resolved_parameter_types):
			effective_type = effective_param.check(context).resolved_type
			if not formal_type.compatible(effective_type):
				raise semantic.SpecificTypeExpected(effective_param.pos,
						"ce paramètre effectif", formal_type, effective_type)
		self.resolved_type = function.resolved_return_type
		return self

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
		self.resolved_type = self.rhs.check(composite.context)
		return self

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
	resolved_type = typedesc.Range

	def check(self, context):
		for operand in (self.lhs, self.rhs):
			operand_type = operand.check(context).resolved_type
			if operand_type is not typedesc.Integer:
				raise semantic.SpecificTypeExpected(operand.pos,
						"une borne d'intervalle",
						expected=typedesc.Integer, given=operand_type)
		return self

class LessThan(BinaryComparisonOp):
	keyword_def = kw.LT

class GreaterThan(BinaryComparisonOp):
	keyword_def = kw.GT

class LessOrEqual(BinaryComparisonOp):
	keyword_def = kw.LE

class GreaterOrEqual(BinaryComparisonOp):
	keyword_def = kw.GE

class Equal(BinaryComparisonOp):
	keyword_def = kw.EQ

class NotEqual(BinaryComparisonOp):
	keyword_def = kw.NE

class LogicalAnd(BinaryLogicalOp):
	keyword_def = kw.AND

class LogicalOr(BinaryLogicalOp):
	keyword_def = kw.OR

class Assignment(BinaryOp):
	keyword_def = kw.ASSIGN
	right_ass = True
	# an assignment cannot be part of another expression, therefore it has no type
	resolved_type = None

	def check(self, context):
		ltype = self.lhs.check(context).resolved_type
		rtype = self.rhs.check(context).resolved_type
		if not ltype.compatible(rtype):
			raise semantic.TypeMismatch(self.rhs.pos, "le type de l'opérande de "
					"droite doit être compatible avec le type de l'opérande de gauche",
					ltype, rtype)
		return self

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

