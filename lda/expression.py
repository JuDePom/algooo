from . import position
from . import kw
from . import dot
from . import types

class Expression(position.SourceThing):
	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

class Varargs(Expression):
	def __init__(self, pos, arg_list):
		super().__init__(pos)
		self.arg_list = arg_list

	def __getitem__(self, index):
		return self.arg_list[index]

	def __iter__(self):
		for arg in self.arg_list:
			yield arg

	def __len__(self):
		return len(self.arg_list)

	def __eq__(self, other):
		return self.arg_list == other.arg_list

	def put_node(self, cluster):
		def make_arg_node(i, item):
			arg_node = dot.Node("arg"+str(i), cluster)
			rhs_node = item.put_node(rhs_cluster)
			arg_node.children.append(rhs_node)
			return arg_node
		if len(self) == 0:
			return dot.Node("\u2205", cluster)
		rhs_cluster = dot.Cluster("", cluster)
		arg_nodes = [ make_arg_node(i, item) for i, item in enumerate(self) ]
		for previous, current in zip(arg_nodes, arg_nodes[1:]):
			previous.children.append(current)
		cluster.rank_chains.append(arg_nodes)
		return arg_nodes[0]

	def lda(self, exp):
		exp.join(self.arg_list, exp.put, ", ")

	def check(self, context, logger):
		self.resolved_type = [arg.check(context, logger) for arg in self]
		return self

class Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value

	def put_node(self, cluster):
		return dot.Node(str(self), cluster)

	def check(self, context, logger):
		return self

class LiteralInteger(Literal):
	resolved_type = types.INTEGER

	def lda(self, exp):
		exp.put(str(self.value))

class LiteralReal(Literal):
	resolved_type = types.REAL

	def lda(self, exp):
		exp.put(str(self.value))

class LiteralString(Literal):
	resolved_type = types.STRING

	def lda(self, exp):
		exp.put(kw.QUOTE2, self.value, kw.QUOTE2)

class LiteralCharacter(Literal):
	resolved_type = types.CHARACTER

	def __init__(self, pos, value):
		super().__init__(pos, value)
		assert len(value) == 1

	def lda(self, exp):
		exp.put(kw.QUOTE1, self.value, kw.QUOTE1)

class LiteralBoolean(Literal):
	resolved_type = types.BOOLEAN

	def lda(self, exp):
		exp.put(kw.TRUE if self.value else kw.FALSE)

