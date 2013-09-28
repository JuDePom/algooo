from . import kw
from . import types
from . import semantictools
from .errors import semantic

class _BaseFunction:
	"""
	Base class for a function with a lexicon and a statement block body.
	"""

	def __init__(self, pos, lexicon, body):
		self.pos = pos
		self.lexicon = lexicon
		self.body = body

	def check(self, context, logger):
		# Push new context onto the context stack, i.e. enter function scope
		context.push(self)
		# Check lexicon
		if self.lexicon is not None:
			self.lexicon.check(context, logger)
		# Check statements
		self.body.check(context, logger)
		# Exit function scope
		context.pop()

	def lda_signature(self, pp):
		"""
		Generate LDA signature for the function. This signature will be output
		right before the function's LDA code block.
		"""
		raise NotImplementedError

	def lda(self, pp):
		self.lda_signature(pp)
		pp.newline()
		if self.lexicon:
			pp.putline(self.lexicon)
		pp.putline(kw.BEGIN)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.put(kw.END)

	def js_signature(self, pp):
		"""
		Generate JS signature for the function. This signature will be output
		right before the function's JS code block.
		"""
		raise NotImplementedError

	def js(self, pp):
		self.js_signature(pp)
		pp.putline(" {")
		if self.lexicon:
			pp.indented(pp.putline, self.lexicon)
		if self.body:
			pp.indented(pp.putline, self.body)
		pp.put("}")


class Algorithm(_BaseFunction):
	"""
	Entry point function that takes no parameters and does not return a value.
	There can only be one algorithm per module.
	"""

	def lda_signature(self, pp):
		pp.put(kw.ALGORITHM)

	def js_signature(self, pp):
		pp.put("P.main = function()")

	def check_return(self, logger, return_statement):
		"""
		Ensure the given return statement does not return an expression, since
		algorithms cannot return anything.
		"""
		if return_statement.expression is not None:
			logger.log(semantic.SemanticError(return_statement.expression.pos,
					"un algorithme ne peut pas retourner une valeur"))


class Function(_BaseFunction):
	"""
	Callable function that has a name, takes zero or more parameters, and may
	return a value. The number of functions in a module is unlimited.
	"""

	def __init__(self, pos, end_pos, ident, fp_list, return_type, lexicon, body):
		super().__init__(pos, lexicon, body)
		self.end_pos     = end_pos
		self.ident       = ident
		self.fp_list     = fp_list
		self.return_type = return_type

	def check_signature(self, context, logger):
		"""
		Run semantic analysis of the function's return type and formal parameters.
		This method sets the `resolved_return_type` attribute.
		"""
		self.resolved_return_type = self.return_type.resolve_type(context, logger)
		for fp in self.fp_list:
			fp.check(context, logger)

	def check(self, context, logger):
		"""
		Ensure the function's lexicon and body are semantically correct.

		This method requires the formal parameters to have been checked,
		therefore `check_signature()` must have been called prior to calling
		this method.
		"""
		# Hunt duplicates among formal parameters
		semantictools.hunt_duplicates(self.fp_list, logger)
		# Ensure each formal parameter matches its declaration in the lexicon,
		# and set the formal flag in the relevant lexicon declarations.
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
		super().check(context, logger)
		# Ensure a return statement can be reached if the signature says the
		# function returns non-VOID
		if self.return_type is not types.VOID and not self.body.returns:
			logger.log(semantic.MissingReturnStatement(self.end_pos))

	def check_effective_parameters(self, context, logger, pos, params):
		"""
		Ensure the given effective parameters can be used in a call to this
		function.

		All parameters are guaranteed to have been checked semantically prior
		to running this method.
		"""
		# check parameter count
		expected_argc = len(self.fp_list)
		given_argc = len(params)
		if expected_argc != given_argc:
			logger.log(semantic.ParameterCountMismatch(pos,
					given=given_argc, expected=expected_argc))
			return
		# check effective parameter types
		for effective, formal in zip(params, self.fp_list):
			semantictools.enforce_compatible("ce paramètre effectif",
					formal.resolved_type, effective, logger)

	def check_return(self, logger, return_statement):
		"""
		Ensure the given return statement can be used within this function's body.

		The return statement's expression is guaranteed to have been checked
		semantically prior to running this method.
		"""
		if return_statement.expression is not None:
			semantictools.enforce_compatible("l'expression retournée",
					self.resolved_return_type, return_statement.expression, logger)
		elif self.return_type is not types.VOID:
			logger.log(semantic.TypeError(return_statement.pos,
					"cette instruction 'retourne' ne renvoit rien alors que la "
					"fonction est censée renvoyer une valeur de type {}".format(
					self.return_type),
					self.return_type))

	def lda_signature(self, pp):
		pp.put(kw.FUNCTION, " ", self.ident, kw.LPAREN)
		pp.join(self.fp_list, pp.put, ", ")
		pp.put(kw.RPAREN)
		if self.return_type is not types.VOID:
			pp.put(kw.COLON, " ", self.return_type)

	def js_signature(self, pp):
		pp.put("P.", self.ident, " = function(")
		prefix = ""
		for formal in self.fp_list:
			pp.put(prefix, "ptr" if formal.js_fakeptr else "", formal.ident)
			prefix = ", "
		pp.put(")")

	def js_call(self, pp, params):
		"""
		Translate an LDA function call to one JavaScript function call.

		This method is intentionally delegated to Function, so that builtin
		functions (which fake a Function interface but aren't actual Function
		instances) can define a more complex `js_call()`.
		"""
		pp.put("P.", self.ident, "(")
		prefix = ""
		for formal, effective in zip(self.fp_list, params):
			pp.put(prefix)
			if formal.js_fakeptr:
				pp.put("LDA.ptr(function(){return ", effective,
						";},function(v){", effective, "=v;})")
			else:
				pp.put(effective)
			prefix = ", "
		pp.put(")")

