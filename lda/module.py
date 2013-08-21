from . import keywords as kw
from . import typedesc
from . import dot
from .errors import semantic
from .statements import StatementBlock

class Module:
	def __init__(self, functions, algorithm=None):
		self.functions = functions
		self.algorithm = algorithm

	def check(self, context=None):
		if context is None:
			context = {}
		supercontext = {f.ident.name: f for f in self.functions}
		for function in self.functions:
			function.check(supercontext)
		if self.algorithm is not None:
			self.algorithm.check(supercontext)
	
	def put_node(self, cluster):
		supercluster = dot.Cluster("module", cluster)
		for f in self.functions:
			f.put_node(supercluster)
		if self.algorithm is not None:
			self.algorithm.put_node(supercluster)

	def lda_format(self, indent=0):
		result = '\n\n'.join(function.lda_format() for function in self.functions)
		if self.algorithm is not None:
			if result != "":
				result += '\n\n'
			result += self.algorithm.lda_format()
		return result

	def js_format(self):
		raise Exception("Faire du JavaScript c'est notre but "
			"mais on n'y est pas encore... choisis un autre format de sortie.")

class Algorithm(StatementBlock):
	def __init__(self, pos, lexicon, body):
		super().__init__(pos, body)
		self.lexicon = lexicon

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
		StatementBlock.check(self, subcontext)

class Function(StatementBlock):
	def __init__(self, pos, ident, fp_list, return_type, lexicon, body):
		super().__init__(pos, body)
		self.ident = ident
		self.fp_list = fp_list
		self.lexicon = lexicon
		self.return_type = return_type

	def check(self, context):
		# check lexicon
		if self.lexicon is None:
			subcontext = context
		else:
			subcontext = self.lexicon.check(context)
		# hunt duplicates among formal parameters
		typedesc._hunt_duplicates(self.fp_list)
		# ensure each formal parameter matches its declaration in the lexicon
		for fp in self.fp_list:
			try:
				fp_type = fp.type_descriptor
				fp_lexicon_type = self.lexicon.symbol_dict[fp.ident.name].type_descriptor
				if fp_type != fp_lexicon_type:
					raise semantic.TypeMismatch(fp.ident.pos, fp_type, fp_lexicon_type)
			except KeyError:
				raise semantic.FormalParameterMissingInLexicon(fp.ident)
		# check statements
		StatementBlock.check(self, subcontext)

	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.ident), cluster)
		return super().put_node(function_cluster)

	def lda_format(self, indent=0):
		# formal parameters
		params = ", ".join(param.lda_format() for param in self.fp_list)
		# return type
		if self.return_type is typedesc.Void:
			return_type = ""
		else:
			return_type = ": {}".format(self.return_type.lda_format())
		# lexicon
		if self.lexicon is None:
			lexicon = ""
		else:
			lexicon = self.lexicon.lda_format(indent+1) + "\n"
		# body
		body = self.body.lda_format(indent+1)
		if body != "":
			body += "\n"
		return ("{kw.FUNCTION} {ident}({params}){return_type}\n"
				"{lexicon}"
				"{kw.BEGIN}\n{body}{kw.END}").format(
						kw = kw,
						ident = self.ident.lda_format(),
						params = params,
						return_type = return_type,
						lexicon = lexicon,
						body = body)

