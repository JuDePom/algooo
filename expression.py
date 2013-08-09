import position
from symboltable import scalars
import dot

class Expression(position.SourceThing):
	pass

class Varargs(Expression):
	def __init__(self, pos, arg_list):
		super().__init__(pos)
		self.arg_list = arg_list

	def __iter__(self):
		for arg in self.arg_list:
			yield arg

	def __len__(self):
		return len(self.arg_list)

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

	def check(self, context):
		return [arg.check(context) for arg in self]

class _Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value

	def __repr__(self):
		return str(self.value)

	def put_node(self, cluster):
		return dot.Node(str(self), cluster)

	def check(self, context):
		return self._typedef

class LiteralInteger(_Literal):
	_typedef = scalars['INT']

class LiteralReal(_Literal):
	_typedef = scalars['REAL']

class LiteralString(_Literal):
	_typedef = scalars['STRING']

	def __repr__(self):
		return "\"" + self.value + "\""

class LiteralBoolean(_Literal):
	_typedef = scalars['BOOL']

