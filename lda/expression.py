from . import kw
from . import dot
from . import types

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
	def __init__(self, pos):
		self.pos = pos
		self.root = False

	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

class Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value

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

