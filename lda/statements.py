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

	def lda(self, pp):
		pp.join(self.body, pp.newline)

	def js(self, pp):
		pp.join(self.body, pp.newline)

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
		rank_chain = []
		prev_node = None
		for i, conditional in enumerate(self.conditionals):
			c_cluster = dot.Cluster("", cluster)
			cond_node = conditional.condition.put_node(c_cluster)
			then_cluster = dot.Cluster("alors", c_cluster)
			then_node = conditional.block.put_node(then_cluster)
			if_node = dot.Node("si" if i == 0 else "snsi", c_cluster, cond_node, then_node)
			rank_chain.append(if_node)
			if prev_node is not None:
				prev_node.children.append(if_node)
			prev_node = if_node
		if self.else_block is not None:
			else_cluster = dot.Cluster("sinon", cluster)
			else_node = self.else_block.put_node(else_cluster)
			prev_node.children.append(else_node)
			rank_chain.append(else_node)
		cluster.rank_chains.append(rank_chain)
		return rank_chain[0]

	def lda(self, pp):
		intro = kw.IF
		for conditional in self.conditionals:
			pp.putline(intro, " ", conditional.condition, " ", kw.THEN)
			pp.indented(pp.putline, conditional.block)
			intro = kw.ELIF
		if self.else_block:
			pp.putline(kw.ELSE)
			pp.indented(pp.putline, self.else_block)
		pp.put(kw.END_IF)

	def js(self, pp):
		intro = "if ( "
		for conditional in self.conditionals:
			pp.putline(intro, conditional.condition, " ) {")
			pp.indented(pp.putline, conditional.block)
			intro = "}else if ( "
		if self.else_block:
			pp.putline("}else {")
			pp.indented(pp.putline, self.else_block)
		pp.put("}")
		
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

	def lda(self, pp):
		pp.putline(kw.FOR, " ", self.counter, " ", kw.FROM, " ", self.initial,
				" ", kw.TO, " ", self.final, " ", kw.DO)
		if self.block:
			pp.indented(pp.putline, self.block)
		pp.put(kw.END_FOR)

	def js(self, pp):
		pp.putline("for", " (", self.counter, "=", self.initial,
				"; ", self.counter, "===", self.final, ";", self.counter, "++){")
		if self.block:
			pp.indented(pp.putline, self.block)
		pp.put("{")

class While(Conditional):
	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("tantque", cluster, cond_node, block_node)

	def lda(self, pp):
		pp.putline(kw.WHILE, " ", self.condition, " ", kw.DO)
		if self.block:
			pp.indented(pp.putline, self.block)
		pp.put(kw.END_WHILE)

	def js(self, pp):
		pp.putline("while", " ( ", self.condition, " )")
		if self.block:
			pp.indented(pp.putline, self.block)

