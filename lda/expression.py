from . import position
from . import typedesc
from . import keywords as kw
from . import dot

class Expression(position.SourceThing):
	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

class Varargs(Expression):
	def __init__(self, pos, arg_list):
		super().__init__(pos)
		self.arg_list = arg_list

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

	def lda_format(self, indent=0):
		return ", ".join(param.lda_format() for param in self.arg_list)
		
	def check(self, context):
		return [arg.check(context) for arg in self]

class _Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value

	def put_node(self, cluster):
		return dot.Node(str(self), cluster)

	def check(self, context):
		return self._typedef

class LiteralInteger(_Literal):
	_typedef = typedesc.Integer

	def lda_format(self, indent=0):
		return str(self.value)

class LiteralReal(_Literal):
	_typedef = typedesc.Real

	def lda_format(self, indent=0):
		return str(self.value)

class LiteralString(_Literal):
	_typedef = typedesc.String

	def lda_format(self, indent=0):
		return '"{}"'.format(self.value)

class LiteralCharacter(_Literal):
	_typedef = typedesc.Character

	def __init__(self, pos, value):
		super().__init__(pos, value)
		assert len(value) == 1

	def lda_format(self, indent=0):
		return "'{}'".format(self.value)

class LiteralBoolean(_Literal):
	_typedef = typedesc.Boolean

	def lda_format(self, indent=0):
		return kw.TRUE.default_spelling if self.value else kw.FALSE.default_spelling

