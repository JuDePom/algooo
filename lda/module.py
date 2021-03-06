from lda.prettyprinter import JSPrettyPrinter, LDAPrettyPrinter
from .lexicon import Lexicon
from .errors import semantic

class Module:
	# All identifiers at the module level will pertain
	# to this "namespace" in the generated JS code.
	js_namespace = "P."

	def __init__(self, lexicon, functions, algorithms):
		variables  = None if lexicon is None else lexicon.variables
		composites = None if lexicon is None else lexicon.composites
		self.lexicon = Lexicon(variables, composites, functions)
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
		# No need to check functions here, it was done by self.lexicon.check()
		context.pop()

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
		pp.putline("// Compiled program namespace")
		pp.putline("var P = {};")
		pp.newline()
		if self.lexicon:
			pp.putline(self.lexicon)
			pp.newline(2)
		for function in self.functions:
			function.js(pp)
			pp.putline(";")
			pp.newline()
		if self.algorithms:
			self.algorithms[0].js(pp)
			pp.putline(";")

	def quicklda(self):
		pp = LDAPrettyPrinter()
		self.lda(pp)
		return str(pp)

	def quickjs(self):
		pp = JSPrettyPrinter()
		self.js(pp)
		return str(pp)