'''
Items that make up the abstract syntax tree.
'''

import dot
import operators as ops
import ldakeywords as kw
from symboltable import SymbolTable
from errors import *

class Module:
	def __init__(self, functions, algorithm=None):
		self.functions = functions
		self.algorithm = algorithm
		self.symbols = SymbolTable(functions=functions)
	def check(self):
		for function in self.functions:
			function.check(self.symbols)
		if self.algorithm is not None:
			self.algorithm.check(self.symbols)

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
	def __eq__(self, other):
		return kw.meta.keyword_equality(self, other)
	def __ne__(self, other):
		return not self.__eq__(other)

class Identifier(Token):
	def __init__(self, pos, name):
		super().__init__(pos)
		self.name = name
	def __eq__(self, other):
		return isinstance(other, Identifier) and self.name == other.name
	def __repr__(self):
		return self.name
	def put_node(self, cluster):
		return dot.Node(str(self), cluster)
	def check(self, context):
		try:
			self.type_spec = context.variables[self.name].type_spec
		except KeyError:
			# TODO - peut-être qu'il serait plus judicieux de logger les erreurs
			# sémantiques que de les lever comme exceptions
			raise MissingDeclaration(self)

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
	def check(self, context):
		for statement in self:
			statement.check(context)

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
	def check(self, context):
		subcontext = SymbolTable.merge(context, self.lexicon)
		for statement in self:
			statement.check(subcontext)

class Function(StatementBlock):
	def __init__(self, pos, ident, fp_list, lexicon, body):
		super().__init__(pos, body)
		self.ident = ident
		self.fp_list = fp_list
		self.lexicon = lexicon
	def __repr__(self):
		return "fonction {} :\n{}\n{}".format(self.ident, self.lexicon, self.body)
	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.ident), cluster)
		return super().put_node(function_cluster)
	def check(self, context):
		subcontext = SymbolTable.merge(context, self.lexicon)
		for statement in self:
			statement.check(subcontext)


#######################################################################
#
# LEXICON
#
#######################################################################

class Lexicon(SourceThing, SymbolTable):
	def __init__(self, pos, variables, molds):
		SourceThing.__init__(self, pos)
		SymbolTable.__init__(self, variables=variables, molds=molds)
		# TODO - pas sûr avec héritage multiple qu'on ait le droit de faire ca ...
		#self.declarations = declarations
		#self.molds = molds
	def __repr__(self):
		return "lexdecl = {}\nlexmolds = {}".format(
				self.variables, self.molds)

class CompoundMold(SourceThing, SymbolTable):
	def __init__(self, ident, fp_list):
		SourceThing.__init__(self, ident.pos)
		SymbolTable.__init__(self, variables=fp_list)
		#super().__init__(ident.pos)
		self.ident = ident
		#self.components = fp_list
	def __repr__(self):
		return "{}={}".format(self.ident, self.variables)

class TypeSpec(SourceThing):
	def __init__(self, type_word, array_dimensions=None):
		pos = None if isinstance(type_word, kw.KeywordDef) else type_word.pos
		super().__init__(pos)
		self.type_word        = type_word
		self.array_dimensions = array_dimensions
		# useful automatic flags
		self.synthetic        = pos is None
		self.mold             = isinstance(type_word, Identifier)
		self.scalar           = not self.mold
		self.array            = self.array_dimensions is not None
		self.pure_mold        = self.mold and not self.array
		self.pure_scalar      = self.scalar and not self.array
		if self.scalar:
			assert(self.type_word in kw.meta.all_scalar_types)
	def make_pure(self):
		return TypeSpec(self.type_word)
	def __eq__(self, other):
		if isinstance(other, kw.KeywordDef):
			return self.pure_scalar and self.type_word == other
		elif not isinstance(other, TypeSpec):
			return False
		return self.type_word == other.type_word and \
				self.array_dimensions == other.array_dimensions
	def __ne__(self, other):
		return not self.__eq__(other)
	def __repr__(self):
		s = str(self.type_word)
		if self.array:
			s = "tableau {}{}".format(s, self.array_dimensions)
		return "TSpec/{:x}/{}".format(id(self), s)

class FormalParameter(SourceThing):
	def __init__(self, ident, type_spec, inout):
		super().__init__(ident.pos)
		self.ident = ident
		self.type_spec = type_spec
		self.inout = inout
	def __repr__(self):
		inout_str = " inout" if self.inout else ""
		return "{}{} : {}".format(self.ident, inout_str, self.type_spec)

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
		arg_nodes = []
		old_arg_node = None
		rhs_cluster = dot.Cluster("", cluster)
		for i, item in enumerate(self):
			arg_node = dot.Node("arg"+str(i), cluster)
			rhs_node = item.put_node(rhs_cluster)
			arg_node.children.append(rhs_node)
			arg_nodes.append(arg_node)
			if old_arg_node is not None:
				old_arg_node.children.append(arg_node)
			old_arg_node = arg_node
		cluster.rank_chains.append(arg_nodes)
		if len(arg_nodes) > 0:
			return arg_nodes[0]
		else:
			return dot.Node("\u2205", cluster)
	def check(self, context):
		for arg in self:
			arg.check(context)

class _Literal(Expression):
	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value
	def __repr__(self):
		return str(self.value)
	def put_node(self, cluster):
		return dot.Node(str(self), cluster)
	def check(self, context):
		pass

class LiteralInteger(_Literal):
	type_spec = TypeSpec(kw.INT)

class LiteralReal(_Literal):
	type_spec = TypeSpec(kw.REAL)

class LiteralString(_Literal):
	type_spec = TypeSpec(kw.STRING)
	def __repr__(self):
		return "\"" + self.value + "\""

class LiteralBoolean(_Literal):
	pass

