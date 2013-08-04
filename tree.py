import dot_export as dot

'''
Items that make up the abstract syntax tree.
'''

class SourceThing:
	'''
	Anything that can represented in a source file.
	'''
	def __init__(self, pos):
		self.pos = pos
	def dot_id(self):
		return "SourceThing_{:08x}".format(id(self))

class Token(SourceThing):
	pass

class KeywordToken(Token):
	def __init__(self, pos, kw_def):
		SourceThing.__init__(self, pos)
		self.kw_def = kw_def

class Identifier(Token):
	def __init__(self, pos, name_string):
		SourceThing.__init__(self, pos)
		self.name_string = name_string
	def __repr__(self):
		return self.name_string
	def put_node(self, cluster):
		return dot.Node(str(self), cluster)

#######################################################################
#
# TOP-LEVEL
#
#######################################################################

class Algorithm(SourceThing):
	def __init__(self, pos, lexicon, body):
		SourceThing.__init__(self, pos)
		self.body = body
		self.lexicon = lexicon
	def __repr__(self):
		return "algorithme :\n{}\n{}".format(self.lexicon, self.body)

class Function(SourceThing):
	def __init__(self, pos, name, fp_list, lexicon, body):
		SourceThing.__init__(self, pos)
		self.name = name
		self.fp_list = fp_list
		self.lexicon = lexicon
		self.body = body
	def __repr__(self):
		return "fonction {} :\n{}\n{}".format(self.name, self.lexicon, self.body)
	def put_node(self, pcluster):
		fcluster = dot.Cluster("fonction " + str(self.name), pcluster)
		#stmt_nodes = []
		prev_outer_node = None
		rank_chain = []
		i = 0
		for statement in self.body:
			ncluster = dot.Cluster("", fcluster)
			node = statement.put_node(ncluster)
			outer_node = dot.Node("statement "+str(i), fcluster)
			outer_node.children.append(node)
			if prev_outer_node is not None:
				prev_outer_node.children.append(outer_node)
			prev_outer_node = outer_node
			rank_chain.append(outer_node)
			i += 1
		#self.lexicon.put_node(fcluster)
		fcluster.rank_chains.append(rank_chain)

#######################################################################
#
# LEXICON
#
#######################################################################

class Lexicon(SourceThing):
	def __init__(self, pos, declarations, molds):
		SourceThing.__init__(self, pos)
		self.declarations = declarations
		self.molds = molds
	def __repr__(self):
		return "lexdecl = {}\nlexmolds = {}".format(
				self.declarations, self.molds)
	def put_node(self, pcluster):
		lcluster = dot.Cluster("lexique", pcluster)
		dcluster = dot.Cluster("déclarations", lcluster)
		for d in self.declarations:
			d.put_node(dcluster)
		mcluster = dot.Cluster("moules", lcluster)
		for m in self.molds:
			m.put_node(mcluster)
		#return dot.Node("lexique",
				#dot.Node("déclarations", *decl_nodes),
				#dot.Node("moules", *mold_nodes))
	
class CompoundMold(SourceThing):
	def __init__(self, name_id, fp_list):
		SourceThing.__init__(self, name_id.pos)
		self.name_id = name_id
		self.components = fp_list
	def __repr__(self):
		return "{}={}".format(self.name_id, self.components)
	def put_node(self, pcluster):
		raise Exception("à faire!!!")
		component_nodes = []
		for c in self.components:
			component_nodes.append(c.dot_node())
		return dot.Node("moule composite " + str(self.name_id), *component_nodes)

class FormalParameter(SourceThing):
	def __init__(self, name, type_, inout, array_dimensions=None):
		SourceThing.__init__(self, name.pos)
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
	def put_node(self, pcluster):
		return dot.Node(str(self), pcluster)

#######################################################################
#
# INSTRUCTIONS
#
#######################################################################

class Instruction(SourceThing):
	def __init__(self, pos):
		SourceThing.__init__(self, pos)

class InstructionIf(Instruction):
	def __init__(self, pos, bool_Expr, first_block, optional_block=None ):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.first_block = first_block
		self.optional_block = optional_block
	def __repr__(self):
		if self.optional_block is None:
			return "si {} alors \n{}fsi\n".format(self.bool_Expr, self.first_block)
		else :
			return "si {} alors \n{}sinon \n{}fsi\n".format(self.bool_Expr, self.first_block, self.optional_block)

class InstructionFor(Instruction):
	def __init__(self, pos, increment, int_from, int_to, block):
		Instruction.__init__(self, pos)
		self.increment = increment
		self.int_from = int_from
		self.int_to = int_to
		self.block = block		
	def __repr__(self):
		return "pour {} de {} a {} faire \n{}fpour\n".format(self.increment, self.int_from, self.int_to, self.block)

class InstructionForEach(Instruction):
	def __init__(self, pos, element, list_element, block):
		Instruction.__init__(self, pos)
		self.element = element
		self.list_element = list_element
		self.block = block	
	def __repr__(self):
		return "pour chaque {} dans {} faire \n{}fpour\n".format(self.element, self.list_element, self.block)

class InstructionWhile(Instruction):
	def __init__(self, pos, bool_Expr, block):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.block = block	
	def __repr__(self):
		return "tantque {} faire \n{}ftant\n".format(self.bool_Expr, self.block)

class InstructionDoWhile(Instruction):
	def __init__(self, pos, block, bool_Expr):
		Instruction.__init__(self, pos)
		self.block = block
		self.bool_Expr = bool_Expr	
	def __repr__(self):
		return "répéter \n{} \njusqu'à {}\n".format(self.block, self.bool_Expr)
		
		
#######################################################################
#
# EXPRESSION COMPONENTS
#
#######################################################################

class Expression(SourceThing):
	pass

class OperatorToken(Token):
	def __init__(self, op_kw, op):
		Token.__init__(self, op_kw.pos)
		self.kw = op_kw
		self.op = op
	def __repr__(self):
		return "o_{}".format(self.op)

class UnaryOpNode(Expression):
	def __init__(self, op_tok, operand):
		Expression.__init__(self, op_tok.pos)
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
		Expression.__init__(self, op_tok.pos)
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
		if type(self.rhs) is not list:
			rhs_node = self.rhs.put_node(pcluster)
		elif len(self.rhs) > 0:
			arg_nodes = []
			old_arg_node = None
			if len(self.rhs) > 1:
				rhs_cluster = dot.Cluster("", pcluster)
			else:
				rhs_cluster = pcluster
			i = 0
			for item in self.rhs:
				arg_node = dot.Node("arg"+str(i), pcluster)
				rhs_node = item.put_node(rhs_cluster)
				arg_node.children.append(rhs_node)
				arg_nodes.append(arg_node)
				if old_arg_node is not None:
					old_arg_node.children.append(arg_node)
				old_arg_node = arg_node
				i += 1
			rhs_node = arg_nodes[0]
			pcluster.rank_chains.append(arg_nodes)
		else:
			rhs_node = None
		op_node = dot.Node(self.operator.symbol.default_spelling,
				pcluster,
				self.lhs.put_node(pcluster),
				rhs_node)
		op_node.shape = "circle"
		return op_node

class _Literal(Expression):
	def __init__(self, pos, value):
		Expression.__init__(self, pos)
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

