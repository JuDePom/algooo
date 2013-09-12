from . import kw
from . import dot
from . import symbols
from . import types
from .errors import semantic
from .statements import StatementBlock

class Module:
	def __init__(self, lexicon, functions, algorithms):
		variables  = None if lexicon is None else lexicon.variables
		composites = None if lexicon is None else lexicon.composites
		self.lexicon = symbols.Lexicon(variables, composites, functions)
		self.functions = functions
		self.algorithms = algorithms

	def check(self, context, logger):
		context.push(self)
		self.lexicon.check(context, logger)
		if len(self.algorithms) > 1:
			for a in self.algorithms[1:]:
				logger.log(semantic.SemanticError(a.pos,
						"il ne peut y avoir qu'un seul algorithme par module"))
		for alg in self.algorithms:
			alg.check(context, logger)
		context.pop()

	def put_node(self, cluster):
		supercluster = dot.Cluster("module", cluster)
		for f in self.functions:
			f.put_node(supercluster)
		if self.algorithms:
			self.algorithms[0].put_node(supercluster)

	def lda(self, pp):
		if self.lexicon:
			pp.putline(self.lexicon)
			pp.newline(2)
		for function in self.functions:
			pp.putline(function)
			pp.newline(2)
		if self.algorithms:
			pp.putline(self.algorithms[0])

	def js(self, pp):
		if self.lexicon:
			pp.putline(self.lexicon)
			pp.newline(2)
		for function in self.functions:
			pp.putline(function)
			pp.newline(2)
		if self.algorithms:
			pp.putline(self.algorithms[0])

class Algorithm:
	def __init__(self, pos, lexicon, body):
		self.pos = pos
		self.lexicon = lexicon
		self.body = body

	def put_node(self, cluster):
		algorithm_cluster = dot.Cluster("algorithme", cluster)
		return self.body.put_node(algorithm_cluster)

	def lda(self, pp):
		pp.putline(kw.ALGORITHM)
		if self.lexicon:
			pp.putline(self.lexicon)
		pp.putline(kw.BEGIN)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.put(kw.END)

	def js(self, pp):
		pp.putline("function Main() {")
		if self.lexicon:
			pp.putline(self.lexicon)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.putline("}")

	def check(self, context, logger):
		context.push(self)
		if self.lexicon is not None:
			self.lexicon.check(context, logger)
		self.body.check(context, logger)
		context.pop()

	def check_return_expression(self, logger, expression):
		if expression is not None:
			logger.log(semantic.SemanticError(expression.pos,
				"un algorithme ne peut pas retourner une valeur"))

class Function:
	def __init__(self, pos, ident, fp_list, return_type, lexicon, body):
		self.pos = pos
		self.ident = ident
		self.fp_list = fp_list
		self.return_type = return_type
		self.lexicon = lexicon
		self.body = body

	def check_signature(self, context, logger):
		self.resolved_return_type = self.return_type.resolve_type(context, logger)
		for fp in self.fp_list:
			fp.check(context, logger)

	def check_fp_lexicon(self, logger):
		"""
		Ensure each formal parameter matches its declaration in the lexicon,
		and set the formal flag in the relevant lexicon declarations.
		"""
		for fp in self.fp_list:
			try:
				fp_lexicon = self.lexicon.symbol_dict[fp.ident.name]
			except (AttributeError, KeyError):
				logger.log(semantic.FormalParameterMissingInLexicon(fp.ident))
				continue
			if fp != fp_lexicon:
				logger.log(semantic.TypeMismatch(fp_lexicon.ident.pos, "le type de ce "
					"paramètre formel doit rester le même dans l'en-tête de la fonction "
					"et dans le lexique de la fonction",
					fp_lexicon.type_descriptor, fp.type_descriptor))
			fp_lexicon.formal = True

	def check(self, context, logger):
		# hunt duplicates among formal parameters
		symbols.hunt_duplicates(self.fp_list, logger)
		# check formal parameter counterparts in lexicon
		self.check_fp_lexicon(logger)
		context.push(self)
		# check lexicon
		if self.lexicon is not None:
			self.lexicon.check(context, logger)
		# check statements
		self.body.check(context, logger)
		context.pop()

	def check_effective_parameters(self, context, logger, pos, params):
		# check parameter count
		expected_argc = len(self.fp_list)
		given_argc = len(params)
		if expected_argc != given_argc:
			logger.log(semantic.ParameterCountMismatch(pos,
					given=given_argc, expected=expected_argc))
			return
		# check effective parameter types
		for effective, formal in zip(params, self.fp_list):
			types.enforce_compatible("ce paramètre effectif",
					formal.resolved_type, effective, logger)

	def check_return_expression(self, logger, expression):
		types.enforce_compatible("l'expression retournée",
				self.resolved_return_type, expression, logger)

	def put_node(self, cluster):
		function_cluster = dot.Cluster("fonction " + str(self.ident), cluster)
		return self.body.put_node(function_cluster)

	def lda(self, pp):
		pp.put(kw.FUNCTION, " ", self.ident, kw.LPAREN)
		pp.join(self.fp_list, pp.put, ", ")
		pp.put(kw.RPAREN)
		if self.return_type is not types.VOID:
			pp.put(kw.COLON, " ", self.return_type)
		pp.newline()
		if self.lexicon:
			pp.putline(self.lexicon)
		pp.putline(kw.BEGIN)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.put(kw.END)
		
	def js(self, pp):
		pp.put("function ", self.ident, "(")
		pp.join(self.fp_list, pp.put, ", ")
		pp.put(") {")
		pp.newline()
		if self.lexicon:
			pp.putline(self.lexicon)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.put("};")

	def js_call(self, pp, call_op):
		pp.put(call_op.lhs, "(")
		pp.join(call_op.rhs, pp.put, ", ")
		pp.put(")")

