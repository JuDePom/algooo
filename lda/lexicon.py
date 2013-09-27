from . import kw
from . import semantictools
from .errors import semantic

class Lexicon:
	"""
	Collection of symbols (variable declarations, composite definitions, and
	function definitions).

	A lexicon is attached to an entity (typically a module, a function or an
	algorithm) and it contains symbols specific to that entity.

	Lexicons are different from plain symbol tables in that symbol tables are
	"passive". Lexicons, on the other hand, handle the semantic analysis of the
	symbols they contain (via the check() method).
	"""

	def __init__(self, variables=None, composites=None, functions=None):
		assert(variables  is None or type(variables)  is list)
		assert(composites is None or type(composites) is list)
		assert(functions  is None or type(functions)  is list)
		self.variables  = variables  if variables  is not None else []
		self.composites = composites if composites is not None else []
		self.functions  = functions  if functions  is not None else []
		self.all_items = sorted(self.variables + self.composites + self.functions,
				key = lambda item: item.ident.pos)
		self.symbol_dict = {item.ident.name: item for item in self.all_items}

	def check(self, context, logger):
		"""
		Augment context with lexicon components
		and run a semantic analysis on all lexicon components.
		"""
		# Hunt duplicates. Note that all_items is sorted by declaration
		# position, which is important to report errors correctly.
		semantictools.hunt_duplicates(self.all_items, logger)
		# prevent overwriting existing names in context
		for name in self.symbol_dict:
			try:
				existing = context[name]
				logger.log(semantic.DuplicateDeclaration(
						self.symbol_dict[name].ident, existing.ident))
			except KeyError:
				pass
		# augment context with the contents of the lexicon so that items can
		# refer to other items in the lexicon
		context.update(self.symbol_dict)
		# Composite check pass 1: check fields (create mini symbol table).
		for composite in self.composites:
			composite.resolve_type(context, logger)
		# Composite check pass 2: detect infinite recursion.
		for composite in self.composites:
			composite.detect_loops(composite, logger)
		# Resolve variable types.
		for variable in self.variables:
			variable.check(context, logger)
		# Resolve function signatures before checking function bodies, so that the
		# functions can call functions defined within this lexicon.
		for function in self.functions:
			function.check_signature(context, logger)
		# Check function bodies at the very end, so that they can use
		# composites and variables in this lexicon.
		for function in self.functions:
			function.check(context, logger)

	def __bool__(self):
		"""
		Return False if the Lexicon does not contain any composites or variables.
		Please note that functions are not accounted for by __bool__!
		"""
		return bool(self.composites) or bool(self.variables)

	def lda(self, pp):
		if not self:
			return
		pp.putline(kw.LEXICON)
		pp.indented(pp.join, self.composites + self.variables, pp.newline)

	def js(self, pp):
		if not self:
			return
		pp.join((self.composites + self.variables), pp.newline)

