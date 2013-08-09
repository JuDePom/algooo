import dot
from statements import StatementBlock
from symboltable import SymbolTable

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
	def __init__(self, pos, ident, fp_list, return_type, lexicon, body):
		super().__init__(pos, body)
		self.ident = ident
		self.fp_list = fp_list
		self.lexicon = lexicon
		self.return_type = return_type

	def __repr__(self):
		return "fonction {} :\n{}\n{}".format(self.ident, self.lexicon, self.body)

	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.ident), cluster)
		return super().put_node(function_cluster)

	def check(self, context):
		if self.lexicon is None:
			subcontext = context
		else:
			subcontext = SymbolTable.merge(context, self.lexicon)
		for statement in self:
			statement.check(subcontext)

