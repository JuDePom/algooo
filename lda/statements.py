from . import kw
from . import dot
from . import types
from . import semantictools
from .errors import semantic

#######################################################################
#
# STATEMENT-RELATED CLASSES
#
#######################################################################

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
		semantictools.enforce("la condition", types.BOOLEAN, self.condition, logger)
		self.block.check(context, logger)


#######################################################################
#
# SELF-CONTAINED STATEMENTS
#
#######################################################################

class Assignment:
	def __init__(self, pos, lhs, rhs):
		self.pos = pos
		self.lhs = lhs
		self.rhs = rhs

	def check(self, context, logger):
		self.lhs.check(context, logger)
		self.rhs.check(context, logger)
		if not self.lhs.writable:
			logger.log(semantic.TypeError(self.lhs.pos,
					"l'opérande de gauche ne peut pas être affectée",
					self.lhs.resolved_type))
			return
		ltype = self.lhs.resolved_type
		rtype = self.rhs.resolved_type
		if not ltype.compatible(rtype):
			logger.log(semantic.TypeMismatch(self.pos, "le type de l'opérande de "
					"droite doit être compatible avec le type de l'opérande de gauche",
					ltype, rtype))

	def lda(self, pp):
		pp.put(self.lhs, " ", kw.ASSIGN, " ", self.rhs)

	def js(self, pp):
		pp.put(self.lhs, " = ", self.rhs, ";")


class Return:
	"""
	Return statement.

	May own an expression or not, in which case self.expression is None.
	"""

	def __init__(self, pos, expr):
		self.pos = pos
		self.expression = expr

	def lda(self, pp):
		pp.put(kw.RETURN)
		if self.expression is not None:
			pp.put(" ", self.expression)

	def js(self, pp):
		if self.expression is not None:
			pp.put("return ", self.expression, ";")
		else:
			pp.put("return;")

	def check(self, context, logger):
		if self.expression is not None:
			self.expression.check(context, logger)
		# The return statement may only occur in a context owned by an algorithm
		# or a function, so if the assertion below fails, we have a compiler bug.
		assert hasattr(context.parent, "check_return"), "please implement check_return()"
		# Even if the expression is None, we still need to pass it on to the
		# parent in order to decide whether an empty return value is OK.
		context.parent.check_return(logger, self)


class FunctionCallWrapper:
	def __init__(self, call_op):
		self.pos = call_op.pos
		self.call_op = call_op

	def lda(self, pp):
		self.call_op.put(pp)

	def js(self, pp):
		pp.put(self.call_op, ";")

	def check(self, context, logger):
		self.call_op.check(context, logger)


#######################################################################
#
# META-STATEMENTS (statements that contain other statements)
#
#######################################################################

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
		intro = "if ("
		for conditional in self.conditionals:
			pp.putline(intro, conditional.condition, ") {")
			pp.indented(pp.putline, conditional.block)
			intro = "} else if ("
		if self.else_block:
			pp.putline("} else {")
			pp.indented(pp.putline, self.else_block)
		pp.put("};")

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
			semantictools.enforce(name, types.INTEGER, comp, logger)
		if not self.counter.writable:
			logger.log(semantic.TypeError(self.counter.pos,
					"le compteur doit être une variable",
					self.counter.resolved_type))
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
		pp.putline("for (", self.counter, " = ", self.initial,
				"; ", self.counter, " <= ", self.final, "; ", self.counter, "++) {")
		if self.block:
			pp.indented(pp.putline, self.block)
		pp.put("};")

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
		pp.putline("while (", self.condition, ") {")
		if self.block:
			pp.indented(pp.putline, self.block)
		pp.put("};")

