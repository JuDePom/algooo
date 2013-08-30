from . import kw
from . import dot
from . import expression
from . import types
from .errors import semantic

class StatementBlock:
	def __init__(self, pos, body):
		self.pos = pos
		self.body = body

	def __iter__(self):
		for statement in self.body:
			yield statement

	def __bool__(self):
		return bool(self.body)

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

	def lda(self, exp):
		exp.join(self.body, exp.newline)
		
	def js(self, exp):
		exp.join(self.body, exp.newline)

	def check(self, context, logger):
		for statement in self:
			statement.check(context, logger)

class Conditional:
	"""
	Statement containing a condition and a statement block. The statement
	block is only executed if the condition is verified.
	"""

	def __init__(self, pos, condition, block):
		self.pos = pos
		self.condition  = condition
		self.block = block

	def check(self, context, logger):
		self.condition.check(context, logger)
		types.enforce("la condition", types.BOOLEAN, self.condition, logger)
		self.block.check(context, logger)

class If:
	def __init__(self, conditionals, else_block=None):
		self.pos = conditionals[0].pos
		self.conditionals = conditionals
		self.else_block = else_block

	def check(self, context, logger):
		for clause in self.conditionals:
			clause.check(context, logger)
		if self.else_block is not None:
			self.else_block.check(context, logger)

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

	def lda(self, exp):
		intro = kw.IF
		for conditional in self.conditionals:
			exp.putline(intro, " ", conditional.condition, " ", kw.THEN)
			exp.indented(exp.putline, conditional.block)
			intro = kw.ELIF
		if self.else_block:
			exp.putline(kw.ELSE)
			exp.indented(exp.putline, self.else_block)
		exp.put(kw.END_IF)

	def js(self, exp):
		intro = "if"
		for conditional in self.conditionals:
			exp.putline(intro, " ", conditional.condition, " {")
			exp.indented(exp.putline, conditional.block)
			intro = "} else if"
		if self.else_block:
			exp.putline("}else {")
			exp.indented(exp.putline, self.else_block)
		exp.put("}")
		
class For:
	_COMPONENT_NAMES = [
			"le compteur de la boucle",
			"la valeur initiale du compteur",
			"la valeur finale du compteur"
	]

	def __init__(self, pos, counter, initial, final, block):
		self.pos = pos
		self.counter = counter
		self.initial = initial
		self.final = final
		self.block = block

	def check(self, context, logger):
		components = [self.counter, self.initial, self.final]
		for comp, name in zip(components, For._COMPONENT_NAMES):
			comp.check(context, logger)
			types.enforce(name, types.INTEGER, comp, logger)
		if isinstance(self.counter, expression.Literal):
			logger.log(semantic.SemanticError(self.counter.pos,
					"le compteur ne peut pas être constant"))
		self.block.check(context, logger)

	def put_node(self, cluster):
		counter_node = self.counter.put_node(cluster)
		initial_node = self.initial.put_node(cluster)
		final_node = self.final.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("pour", cluster, counter_node, initial_node,
				final_node, block_node)

	def lda(self, exp):
		exp.putline(kw.FOR, " ", self.counter, " ", kw.FROM, " ", self.initial,
				" ", kw.TO, " ", self.final, " ", kw.DO)
		if self.block:
			exp.indented(exp.putline, self.block)
		exp.put(kw.END_FOR)

	def js(self, exp):
		exp.putline("for", " (", self.counter, "=", self.initial,
				"; ", self.counter, "===", self.final, ";", self.counter, "++){")
		if self.block:
			exp.indented(exp.putline, self.block)
		exp.put("{")

class While(Conditional):
	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("tantque", cluster, cond_node, block_node)

	def lda(self, exp):
		exp.putline(kw.WHILE, " ", self.condition, " ", kw.DO)
		if self.block:
			exp.indented(exp.putline, self.block)
		exp.put(kw.END_WHILE)
	
	def js(self, exp):
		exp.putline("while", " (", self.condition, ")")
		if self.block:
			exp.indented(exp.putline, self.block)

