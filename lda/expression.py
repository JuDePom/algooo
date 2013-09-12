from . import kw
from . import dot
from . import types
from .identifier import PureIdentifier
from .errors import semantic

def surround(lda_method):
	"""
	Surround the exported LDA code with parentheses if the object is not the
	root node of an expression.

	Meant to be used as a decorator for `lda` methods in Expression subclasses.
	"""
	def wrapper(self, pp):
		if self.root:
			lda_method(self, pp)
		else:
			pp.put("(")
			lda_method(self, pp)
			pp.put(")")
	return wrapper

class Expression:
	"""
	Base class for all expressions.

	An expression may stand alone or be built of one or more expressions.

	An expression is a "root" expression if it is not contained by any
	expression. The `root` attribute is set to `False` by default.

	An expression must be checked for semantic correctness with the `check()`
	method. If the semantic analysis is successful, the expression gains the
	`resolved_type` attribute. Otherwise, `resolved_type` is set to a
	`BlackHole` type (typically `ERRONEOUS`).

	Expressions are not writable by default, i.e. they cannot legally occupy in
	the lefthand side of an assignment operation. However, this behavior can be
	overridden by some subclasses, e.g. the array subscript operator.
	"""

	writable = False

	def __init__(self, pos):
		self.pos = pos
		self.root = False

	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

	def check(self, context, logger):
		"""
		Check for semantic aberrations and set the resolved_type attribute.
		"""
		raise NotImplementedError

class ExpressionIdentifier(PureIdentifier, Expression):
	"""
	Name bound to a symbol during the semantic analysis phase.
	"""

	def check(self, context, logger):
		"""
		Resolve the name in the current context's symbol table.

		The `bound` attribute is set to the object referred to by the name.

		The `resolved_type` attribute is set to:
		- `ERRONEOUS` if the name is absent from the symbol table;
		- `NOT_A_VARIABLE` if the name refers to a non-variable object such as
		a composite or a function.
		"""
		# find corresponding symbol in the context's symbol table
		try:
			self.bound = context[self.name]
		except KeyError:
			logger.log(semantic.MissingDeclaration(self))
			self.resolved_type = types.ERRONEOUS
			self.writable = False
			return
		# steal the symbol's type
		try:
			self.resolved_type = self.bound.resolved_type
		except AttributeError:
			# only variable declarations have a resolved_type
			self.resolved_type = types.NOT_A_VARIABLE
		# steal the symbol's writability
		try:
			self.writable = self.bound.writable
		except AttributeError:
			self.writable = False

class Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value

	def __repr__(self):
		return "littéral {}".format(self.resolved_type)

	def put_node(self, cluster):
		return dot.Node(str(self.value), cluster)

	def check(self, context, logger):
		pass

class LiteralInteger(Literal):
	resolved_type = types.INTEGER

	def lda(self, pp):
		pp.put(str(self.value))
	
	def js(self, pp):
		pp.put(str(self.value))

class LiteralReal(Literal):
	resolved_type = types.REAL

	def lda(self, pp):
		pp.put(str(self.value))
		
	def js(self, pp):
		pp.put(str(self.value))

class LiteralString(Literal):
	resolved_type = types.STRING

	def lda(self, pp):
		pp.put(kw.QUOTE2, self.value, kw.QUOTE2)
	
	def js(self, pp):
		pp.put('\"', self.value, '\"')

class LiteralCharacter(Literal):
	resolved_type = types.CHARACTER

	def __init__(self, pos, value):
		super().__init__(pos, value)
		assert len(value) == 1

	def lda(self, pp):
		pp.put(kw.QUOTE1, self.value, kw.QUOTE1)
		
	def js(self, pp):
		pp.put("\'", self.value, "\'")

class LiteralBoolean(Literal):
	resolved_type = types.BOOLEAN

	def lda(self, pp):
		pp.put(kw.TRUE if self.value else kw.FALSE)
		
	def js(self, pp):
		pp.put("true" if self.value else "false")

