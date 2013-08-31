from . import kw
from . import dot
from . import types

class Expression:
	def __init__(self, pos):
		self.pos = pos

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

	def lda(self, exp):
		exp.put(str(self.value))
	
	def js(self, exp):
		exp.put(str(self.value))

class LiteralReal(Literal):
	resolved_type = types.REAL

	def lda(self, exp):
		exp.put(str(self.value))
		
	def js(self, exp):
		exp.put(str(self.value))

class LiteralString(Literal):
	resolved_type = types.STRING

	def lda(self, exp):
		exp.put(kw.QUOTE2, self.value, kw.QUOTE2)
	
	def js(self, exp):
		exp.put('\"', self.value, '\"')

class LiteralCharacter(Literal):
	resolved_type = types.CHARACTER

	def __init__(self, pos, value):
		super().__init__(pos, value)
		assert len(value) == 1

	def lda(self, exp):
		exp.put(kw.QUOTE1, self.value, kw.QUOTE1)
		
	def js(self, exp):
		exp.put("\'", self.value, "\'")

class LiteralBoolean(Literal):
	resolved_type = types.BOOLEAN

	def lda(self, exp):
		exp.put(kw.TRUE if self.value else kw.FALSE)
		
	def js(self, exp):
		exp.put("true" if self.value else "false")

