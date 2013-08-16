import keywords as kw
import dot
from statements import StatementBlock
import typedesc

class Module:
	def __init__(self, functions, algorithm=None):
		self.functions = functions
		self.algorithm = algorithm

	def check(self):
		supercontext = {f.ident.name: f for f in self.functions}
		for function in self.functions:
			function.check(supercontext)
		if self.algorithm is not None:
			self.algorithm.check(supercontext)
	
	def lda_format(self, indent=0):
		result = ""
		for function in self.functions:
			result += function.lda_format()
		if self.algorithm is not None:
			result += self.algorithm.lda_format()
		return result

class Algorithm(StatementBlock):
	def __init__(self, pos, lexicon, body):
		super().__init__(pos, body)
		self.lexicon = lexicon

	def __repr__(self):
		return "algorithme :\n{}\n{}".format(self.lexicon, self.body)

	def put_node(self, cluster):
		algorithm_cluster = dot.Cluster("algorithme", cluster)
		return super().put_node(algorithm_cluster)

	def lda_format(self, indent=0):
		return "{kw.ALGORITHM}\n{lexicon}\n{kw.BEGIN}\n{body}\n{kw.END}".format(
				kw = kw,
				lexicon = self.lexicon.lda_format(indent+1),
				body = self.body.lda_format(indent+1))

	def check(self, context):
		if self.lexicon is None:
			subcontext = context
		else:
			subcontext = self.lexicon.check(context)
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

	def lda_format(self, indent=0):
		params = ", ".join(param.lda_format() for param in self.fp_list)
		
		if self.return_type is typedesc.Void:
			return_type = ""
		else:
			return_type = ": {}".format(self.return_type.lda_format())

		return ("{kw.FUNCTION} {ident}({params}){return_type}\n"
				"{lexicon}\n"
				"{kw.BEGIN}\n{body}\n{kw.END}").format(
						kw = kw,
						ident = self.ident.lda_format(),
						params = params,
						return_type = return_type,
						lexicon = self.lexicon.lda_format(indent+1),
						body = self.body.lda_format(indent+1)
					)

	check = Algorithm.check

