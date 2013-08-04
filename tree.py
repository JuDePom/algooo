import dot

'''
Items that make up the abstract syntax tree.
'''

class SourceThing:
	'''
	Anything that can represented in a source file.
	'''
	def __init__(self, pos):
		self.pos = pos

class Token(SourceThing):
	pass

class KeywordToken(Token):
	def __init__(self, pos, kw_def):
		super().__init__(pos)
		self.kw_def = kw_def

class Identifier(Token):
	def __init__(self, pos, name_string):
		super().__init__(pos)
		self.name_string = name_string
	def __repr__(self):
		return self.name_string
	def put_node(self, cluster):
		return dot.Node(str(self), cluster)

class StatementBlock(SourceThing):
	def __init__(self, pos, body):
		super().__init__(pos)
		self.body = body
	def __iter__(self):
		for statement in self.body:
			yield statement
	def put_node(self, cluster):
		prev_outer_node = None
		first_outer_node = None
		rank_chain = []
		for i, statement in enumerate(self):
			ncluster = dot.Cluster("", cluster)
			node = statement.put_node(ncluster)
			outer_node = dot.Node("statement "+str(i), cluster)
			outer_node.children.append(node)
			if prev_outer_node is not None:
				prev_outer_node.children.append(outer_node)
			else:
				first_outer_node = outer_node
			prev_outer_node = outer_node
			rank_chain.append(outer_node)
		cluster.rank_chains.append(rank_chain)
		return first_outer_node

#######################################################################
#
# TOP-LEVEL
#
#######################################################################

class Algorithm(StatementBlock):
	def __init__(self, pos, lexicon, body):
		super().__init__(pos, body)
		self.lexicon = lexicon
	def __repr__(self):
		return "algorithme :\n{}\n{}".format(self.lexicon, self.body)
	def put_node(self, cluster):
		algorithm_cluster = dot.Cluster("algorithme", cluster)
		return super().put_node(algorithm_cluster)

class Function(StatementBlock):
	def __init__(self, pos, name, fp_list, lexicon, body):
		super().__init__(pos, body)
		self.name = name
		self.fp_list = fp_list
		self.lexicon = lexicon
	def __repr__(self):
		return "fonction {} :\n{}\n{}".format(self.name, self.lexicon, self.body)
	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.name), cluster)
		return super().put_node(function_cluster)

#######################################################################
#
# LEXICON
#
#######################################################################

class Lexicon(SourceThing):
	def __init__(self, pos, declarations, molds):
		super().__init__(pos)
		self.declarations = declarations
		self.molds = molds
	def __repr__(self):
		return "lexdecl = {}\nlexmolds = {}".format(
				self.declarations, self.molds)
	
class CompoundMold(SourceThing):
	def __init__(self, name_id, fp_list):
		super().__init__(name_id.pos)
		self.name_id = name_id
		self.components = fp_list
	def __repr__(self):
		return "{}={}".format(self.name_id, self.components)

class FormalParameter(SourceThing):
	def __init__(self, name, type_, inout, array_dimensions=None):
		super().__init__(name.pos)
		self.name = name
		self.type_ = type_
		self.inout = inout
		self.array_dimensions = array_dimensions
		# useful automatic flags
		self.custom_type = type(type_) is Identifier
		self.scalar = not self.custom_type
		self.array = self.array_dimensions is not None
	def __repr__(self):
		inout_str = "inout " if self.inout else ""
		if self.array:
			return "{}: {}tableau {}{}".format(\
					self.name, inout_str, self.type_, self.array_dimensions)
		else:
			return "{}: {}{}".format(self.name, inout_str, self.type_)

#######################################################################
#
# INSTRUCTIONS
#
#######################################################################

class Instruction(SourceThing):
	pass

class InstructionIf(Instruction):
	def __init__(self, pos, condition, then_block, else_block=None):
		super().__init__(pos)
		self.condition = condition
		self.then_block = then_block
		self.else_block = else_block
	def __repr__(self):
		if self.else_block is None:
			return "si {} alors \n{}fsi\n".format(
					self.condition, self.then_block)
		else :
			return "si {} alors \n{}sinon \n{}fsi\n".format(
					self.condition, self.then_block, self.else_block)
	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		then_cluster = dot.Cluster("alors", cluster)
		then_node = self.then_block.put_node(then_cluster)
		children = [cond_node, then_node]
		if self.else_block is not None:
			else_cluster = dot.Cluster("sinon", cluster)
			else_node = self.else_block.put_node(else_cluster)
			children.append(else_node)
		return dot.Node("si", cluster, *children)

class InstructionFor(Instruction):
	def __init__(self, pos, counter, initial, final, block):
		super().__init__(pos)
		self.counter = counter
		self.initial = initial
		self.final = final
		self.block = block
	def __repr__(self):
		return "pour {} de {} a {} faire \n{}fpour\n".format(
				self.counter, self.initial, self.final, self.block) 
	def put_node(self, cluster):
		counter_node = self.counter.put_node(cluster)
		initial_node = self.initial.put_node(cluster)
		final_node = self.final.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("pour", cluster, counter_node, initial_node,
				final_node, block_node)

class InstructionForEach(Instruction):
	def __init__(self, pos, element, list_element, block):
		super().__init__(pos)
		self.element = element
		self.list_element = list_element
		self.block = block	
	def __repr__(self):
		return "pourchaque {} dans {} faire \n{}fpour\n".format(
				self.element, self.list_element, self.block)

class InstructionWhile(Instruction):
	def __init__(self, pos, condition, block):
		super().__init__(pos)
		self.condition = condition
		self.block = block	
	def __repr__(self):
		return "tantque {} faire \n{}ftant\n".format(self.condition, self.block)
	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("tantque", cluster, cond_node, block_node)

class InstructionDoWhile(Instruction):
	def __init__(self, pos, block, condition):
		super().__init__(pos)
		self.block = block
		self.condition = condition	
	def __repr__(self):
		return "répéter \n{} \njusqu'à {}\n".format(self.block, self.condition)
		
#######################################################################
#
# EXPRESSION COMPONENTS
#
#######################################################################

class Expression(SourceThing):
	pass

class OperatorToken(Token):
	def __init__(self, op_kw, op):
		super().__init__(op_kw.pos)
		self.kw = op_kw
		self.op = op
	def __repr__(self):
		return "o_{}".format(self.op)

class UnaryOpNode(Expression):
	def __init__(self, op_tok, operand):
		super().__init__(op_tok.pos)
		self.operator_token = op_tok
		self.operator = op_tok.op
		self.operand = operand
	def __repr__(self):
		return "({}{})".format(
				self.operator.symbol.default_spelling, 
				self.operand)
	def put_node(self, pcluster):
		op_node = dot.Node(self.operator.symbol.default_spelling,
				pcluster,
				self.operand.put_node(pcluster))
		op_node.shape = "circle"
		return op_node

class BinaryOpNode(Expression):
	def __init__(self, op_tok, lhs, rhs):
		super().__init__(op_tok.pos)
		self.operator_token = op_tok
		self.operator = op_tok.op
		self.lhs = lhs
		self.rhs = rhs
	def __repr__(self):
		return "({1}{0}{2})".format(
				self.operator.symbol.default_spelling, 
				self.lhs, 
				self.rhs)
	def put_node(self, pcluster):
		op_node = dot.Node(self.operator.symbol.default_spelling,
				pcluster,
				self.lhs.put_node(pcluster),
				self.rhs.put_node(pcluster))
		op_node.shape = "circle"
		return op_node

class Varargs(Expression):
	def __init__(self, pos, arg_list):
		super().__init__(pos)
		self.arg_list = arg_list
	def put_node(self, pcluster):
		arg_nodes = []
		old_arg_node = None
		rhs_cluster = dot.Cluster("", pcluster)
		for i, item in enumerate(self.arg_list):
			arg_node = dot.Node("arg"+str(i), pcluster)
			rhs_node = item.put_node(rhs_cluster)
			arg_node.children.append(rhs_node)
			arg_nodes.append(arg_node)
			if old_arg_node is not None:
				old_arg_node.children.append(arg_node)
			old_arg_node = arg_node
		pcluster.rank_chains.append(arg_nodes)
		if len(arg_nodes) > 0:
			return arg_nodes[0]
		else:
			return dot.Node("\u2205", pcluster)

class _Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value
	def __repr__(self):
		return str(self.value) 
	def put_node(self, pcluster):
		return dot.Node(str(self), pcluster)

class LiteralInteger(_Literal):
	pass

class LiteralReal(_Literal):
	pass

class LiteralString(_Literal):
	def __repr__(self):
		return "\"" + self.value + "\""

class LiteralBoolean(_Literal):
	pass

