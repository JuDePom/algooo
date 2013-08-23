from . import keywords as kw
from . import typedesc
from . import dot
from .errors import semantic
from .statements import StatementBlock

class Module(typedesc.Lexicon):
	def __init__(self, variables, composites, functions, algorithms):
		super().__init__(variables, composites, functions)
		self.algorithms = algorithms

	def check(self, context=None):
		subcontext = super().check(context)
		if len(self.algorithms) > 1:
			for a in self.algorithms[1:]:
				# TODO log these errors
				raise semantic.SemanticError(a.pos,
						"il ne peut y avoir qu'un seul algorithme par module")
		elif len(self.algorithms) == 1:
			self.algorithms[0].check(subcontext)

	def put_node(self, cluster):
		supercluster = dot.Cluster("module", cluster)
		for f in self.functions:
			f.put_node(supercluster)
		if self.algorithms:
			self.algorithms[0].put_node(supercluster)

	def lda_format(self, indent=0):
		result = '\n\n'.join(function.lda_format() for function in self.functions)
		if self.algorithms:
			if result != "":
				result += '\n\n'
			result += self.algorithms[0].lda_format()
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

	def check_signature(self, context):
		subcontext = context.copy()
		for fp in self.fp_list:
			subcontext[fp.ident.name] = fp
		self.resolved_return_type = self.return_type.check(subcontext)
		self.resolved_parameter_types = []
		for fp in self.fp_list:
			self.resolved_parameter_types.append(fp.type_descriptor.check(subcontext).resolved_type)

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
				fp_lexicon = self.lexicon.symbol_dict[fp.ident.name]
				fp_lexicon_type = fp_lexicon.type_descriptor
				if fp_type != fp_lexicon_type:
					raise semantic.TypeMismatch(fp_lexicon.ident.pos, "le type de ce paramètre "
						"formel doit rester le même dans l'en-tête de la fonction et dans "
						"le lexique de la fonction", fp_lexicon_type, fp_type)
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

