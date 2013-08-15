import keywords as kw
import position
import dot

class Statement(position.SourceThing):
	pass

class StatementBlock(position.SourceThing):
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
	def lda_format(self, indent=0):
		result = ""
		for statement in self.body:
			result += indent*'\t' + statement.lda_format(indent + 1) + "\n"
		return result
	def check(self, context):
		for statement in self:
			statement.check(context)

class IfThenElse(Statement):
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
	def lda_format(self, indent=0):
		if self.else_block is None:
			return indent*'\t' + "{} {} {}\n{}{}\n".format(
				kw.IF.lda_format(), self.condition.lda_format(), kw.THEN.lda_format(),
				self.then_block.lda_format(indent + 1),
				kw.END_IF.lda_format())
		else :
			return indent*'\t' + "{} {} {}\n{}{}\n{}{}\n".format(
				kw.IF.lda_format(), self.condition.lda_format(), kw.THEN.lda_format(),
				self.then_block.lda_format(indent + 1),
				kw.ELSE.lda_format(),
				self.else_block.lda_format(indent + 1),
				kw.END_IF.lda_format())

class For(Statement):
	def __init__(self, pos, counter, initial, final, block):
		super().__init__(pos)
		self.counter = counter
		self.initial = initial
		self.final = final
		self.block = block
	def __repr__(self):
		return "pour {} de {} a {} faire\n{}fpour\n".format(
				self.counter, self.initial, self.final, self.block)
	def put_node(self, cluster):
		counter_node = self.counter.put_node(cluster)
		initial_node = self.initial.put_node(cluster)
		final_node = self.final.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("pour", cluster, counter_node, initial_node,
				final_node, block_node)
	def lda_format(self, indent=0):
		return indent*'\t' + "{} {} {} {} {} {} {}\n{}{}\n".format(
			kw.FOR.lda_format(), self.counter.lda_format(), kw.FROM.lda_format(), self.initial.lda_format(), kw.TO.lda_format(), self.final.lda_format(), kw.DO.lda_format(),
			self.block.lda_format(indent + 1),
			kw.END_FOR.lda_format())
				
class ForEach(Statement):
	def __init__(self, pos, element, list_element, block):
		super().__init__(pos)
		self.element = element
		self.list_element = list_element
		self.block = block	
	def __repr__(self):
		return "pourchaque {} dans {} faire\n{}fpour\n".format(
				self.element, self.list_element, self.block)

class While(Statement):
	def __init__(self, pos, condition, block):
		super().__init__(pos)
		self.condition = condition
		self.block = block	
	def __repr__(self):
		return "tantque {} faire\n{}ftant\n".format(self.condition, self.block)
	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("tantque", cluster, cond_node, block_node)
	def lda_format(self, indent=0):
		return indent*'\t' + "{} {} {}\n{}{}\n".format(
			kw.WHILE.lda_format(), self.condition.lda_format(), kw.DO.lda_format(),
			self.block.lda_format(indent + 1),
			kw.END_WHILE.lda_format())

class DoWhile(Statement):
	def __init__(self, pos, block, condition):
		super().__init__(pos)
		self.block = block
		self.condition = condition	
	def __repr__(self):
		return "répéter \n{} \njusqu'à {}\n".format(self.block, self.condition)

