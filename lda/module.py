from . import keywords as kw
from . import typedesc
from . import dot
from .errors import semantic
from .statements import StatementBlock

class Module:
	def __init__(self, lexicon, functions, algorithms):
		variables  = None if lexicon is None else lexicon.variables
		composites = None if lexicon is None else lexicon.composites
		self.lexicon = typedesc.Lexicon(variables, composites, functions)
		self.functions = functions
		self.algorithms = algorithms

	def check(self, context=None):
		subcontext = self.lexicon.check(context)
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

	def lda(self, exp):
		if self.lexicon:
			exp.putline(self.lexicon)
			exp.newline(2)
		for function in self.functions:
			exp.putline(function)
			exp.newline(2)
		if self.algorithms:
			exp.putline(self.algorithms[0])

	def js_format(self):
		raise Exception("Faire du JavaScript c'est notre but "
			"mais on n'y est pas encore... choisis un autre format de sortie.")

class Algorithm:
	def __init__(self, pos, lexicon, body):
		self.pos = pos
		self.lexicon = lexicon
		self.body = body

	def put_node(self, cluster):
		algorithm_cluster = dot.Cluster("algorithme", cluster)
		return self.body.put_node(algorithm_cluster)

	def lda(self, exp):
		exp.putline(kw.ALGORITHM)
		if self.lexicon:
			exp.putline(self.lexicon)
		exp.putline(kw.BEGIN)
		if self.body:
			exp.indented(exp.putline, self.body)
		exp.put(kw.END)

	def check(self, context):
		if self.lexicon is None:
			subcontext = context
		else:
			subcontext = self.lexicon.check(context)
		self.body.check(subcontext)

class Function:
	def __init__(self, pos, ident, fp_list, return_type, lexicon, body):
		self.pos = pos
		self.ident = ident
		self.fp_list = fp_list
		self.return_type = return_type
		self.lexicon = lexicon
		self.body = body

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
		self.body.check(subcontext)

	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.ident), cluster)
		return self.body.put_node(function_cluster)

	def lda(self, exp):
		exp.put(kw.FUNCTION, " ", self.ident, kw.LPAREN)
		exp.join(self.fp_list, exp.put, ", ")
		exp.put(kw.RPAREN)
		if self.return_type is not typedesc.Void:
			exp.put(kw.COLON, " ", self.return_type)
		exp.newline()
		if self.lexicon:
			exp.putline(self.lexicon)
		exp.putline(kw.BEGIN)
		if self.body:
			exp.indented(exp.putline, self.body)
		exp.put(kw.END)

