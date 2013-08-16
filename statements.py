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
		indent_string = indent*'\t'
		st_formats = (st.lda_format(indent+1) for st in self.body)
		result = ("\n"+indent_string).join(st_formats)
		if result != "":
			result = indent_string + result
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
		indent_string = indent * '\t'
		result = "{indent}{kw.IF} {condition} {kw.THEN}\n{then_block}\n".format(
				kw = kw,
				indent = indent_string,
				condition = self.condition.lda_format(),
				then_block = self.then_block.lda_format(indent+1))
		if self.else_block is not None:
			result += "{indent}{kw.ELSE}\n{else_block}\n".format(
					kw = kw,
					indent = indent_string,
					else_block = self.else_block.lda_format(indent+1))
		result += "{indent}{kw.END_IF}".format(indent=indent_string, kw=kw)
		return result

class For(Statement):
	def __init__(self, pos, counter, initial, final, block):
		super().__init__(pos)
		self.counter = counter
		self.initial = initial
		self.final = final
		self.block = block

	def put_node(self, cluster):
		counter_node = self.counter.put_node(cluster)
		initial_node = self.initial.put_node(cluster)
		final_node = self.final.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("pour", cluster, counter_node, initial_node,
				final_node, block_node)
	def lda_format(self, indent=0):
		return ("{indent}{kw.FOR} {counter} {kw.FROM} {initial} "
				"{kw.TO} {final} {kw.DO}\n"
				"{block}\n"
				"{indent}{kw.END_FOR}").format(
						kw = kw,
						indent = indent*'\t',
						counter = self.counter.lda_format(),
						initial = self.initial.lda_format(),
						final = self.final.lda_format(),
						block = self.block.lda_format(indent + 1))

class While(Statement):
	def __init__(self, pos, condition, block):
		super().__init__(pos)
		self.condition = condition
		self.block = block	

	def put_node(self, cluster):
		cond_node = self.condition.put_node(cluster)
		block_cluster = dot.Cluster("faire", cluster)
		block_node = self.block.put_node(block_cluster)
		return dot.Node("tantque", cluster, cond_node, block_node)

	def lda_format(self, indent=0):
		return ("{indent}{kw.WHILE} {condition} {kw.DO}\n"
				"{block}\n"
				"{indent}{kw.END_WHILE}").format(
						kw = kw,
						indent = indent*'\t',
						condition = self.condition.lda_format(),
						block = self.block.lda_format(indent + 1))

