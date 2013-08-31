from . import kw
from . import dot
from .types import ERRONEOUS, Composite, Inout
from .errors import semantic

def hunt_duplicates(item_list, logger):
	"""
	Log DuplicateDeclaration for any item using a name already used by another
	item in the list.
	"""
	seen = {}
	for item in item_list:
		name = item.ident.name
		try:
			pioneer = seen[name]
			logger.log(semantic.DuplicateDeclaration(item.ident, pioneer.ident))
		except KeyError:
			seen[name] = item

class Identifier:
	"""
	Name that refers to a symbol in the symbol table.
	"""

	def __init__(self, pos, name):
		self.pos = pos
		self.name = name

	def __repr__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return self.name != other.name

	def lda(self, exp):
		exp.put(self.name)

	def js(self, exp):
		exp.put(self.name)

	def put_node(self, cluster):
		return dot.Node(self.name, cluster)

	def check(self, context, logger):
		try:
			# TODO est-ce qu'on devrait rajouter ErroneousType dans le contexte, histoire de ne pas répéter la même erreur 5000 fois ?
			symbol = context[self.name]
			self.resolved_type = symbol.resolved_type
		except KeyError:
			logger.log(semantic.MissingDeclaration(self))

class TypeAlias(Identifier):
	"""
	Identifier that can only refer to a Composite.
	"""

	def check(self, context, logger):
		# guilty until proven innocent
		self.resolved_type = ERRONEOUS
		try:
			symbol = context[self.name]
		except KeyError:
			logger.log(semantic.UnresolvableTypeAlias(self))
			return
		if isinstance(symbol, Composite):
			self.resolved_type = symbol
		else:
			logger.log(semantic.SpecificTypeExpected(self.pos,
					"cet alias", Composite, type(symbol)))

class Field:
	"""
	Variable declaration. Has an identifier, a type_descriptor and a formal flag
	(i.e. formal parameter).
	Semantically, only formal variables may have the Inout type.
	"""

	def __init__(self, ident, type_descriptor, formal=False):
		self.ident = ident
		self.type_descriptor = type_descriptor
		self.formal = formal

	def __eq__(self, other):
		if self is other:
			return True
		return self.ident == other.ident and \
				self.type_descriptor == other.type_descriptor

	def check(self, context, logger):
		if not self.formal and isinstance(self.type_descriptor, Inout):
			logger.log(semantic.SemanticError(self.ident.pos,
					"\"inout\" n'est autorisé que dans un paramètre formel"))
		self.type_descriptor.check(context, logger)
		self.resolved_type = self.type_descriptor.resolved_type

	def lda(self, exp):
		exp.put(self.ident, kw.COLON, " ", self.type_descriptor)

	def js(self, exp):
		exp.put("var ", self.ident)

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

	def check(self, supercontext, logger):
		"""
		Return supercontext augmented with lexicon components.
		"""
		# initialize supercontext if needed
		if supercontext is None:
			supercontext = {}
		# Hunt duplicates. Note that all_items is sorted by declaration
		# position, which is important to report errors correctly.
		hunt_duplicates(self.all_items, logger)
		# TODO : optionnellement, avertir si on écrase un nom du scope au-dessus
		# fill subcontext with the contents of the lexicon so that items can
		# refer to other items in the lexicon
		subcontext = supercontext.copy()
		subcontext.update({c.ident.name: c for c in self.composites})
		subcontext.update({f.ident.name: f for f in self.functions})
		subcontext.update({v.ident.name: v for v in self.variables})
		# refine composite subcontexts
		for composite in self.composites:
			composite.check(subcontext, logger)
		# resolve function signatures before function bodies,  so that the
		# functions can call functions defined within this lexicon
		for function in self.functions:
			function.check_signature(subcontext, logger)
		# Function pass 2: bodies.
		for function in self.functions:
			function.check(subcontext, logger)
		# resolve variable types
		for variable in self.variables:
			variable.check(subcontext, logger)
		# detect infinite recursion in composites
		for composite in self.composites:
			composite.detect_loops(composite, logger)
		return subcontext

	def __bool__(self):
		"""
		Return False if the Lexicon does not contain any composites or variables.
		Please note that functions are not accounted for by __bool__!
		"""
		return bool(self.composites) or bool(self.variables)

	def lda(self, exp):
		if not self:
			return
		exp.putline(kw.LEXICON)
		exp.indented(exp.join, self.composites + self.variables, exp.newline)

	def js(self, exp):
		if not self:
			return
		exp.indented(exp.join, self.composites + self.variables, exp.newline)

