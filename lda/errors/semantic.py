"""
Semantic errors that can be raised during the semantic analysis phase.
"""

class SemanticError(Exception):
	"""
	Raised when the semantic analysis on a given element fails.

	This happens when the user writes syntactically correct code which will
	invariably fail to produce a working program.

	SemanticErrors are relevant by default, but this can be overridden by
	subclass constructors. Being relevant means that the error is the first to
	relate to the erroneous object. It can happen that a cascade of semantic
	errors are triggered by a single erroneous statement in the source code;
	typically, we only want to log the error pertaining to that statement, and
	ignore all errors that ensue.
	"""
	def __init__(self, pos, message):
		self.pos = pos
		message = "{}: {}".format(pos.pretty(), message)
		super().__init__(message)
		self.relevant = True

class MissingDeclaration(SemanticError):
	"""
	Raised when an identifier is used in a statement without having been declared
	in the current context.
	"""
	def __init__(self, ident):
		message = "cet identificateur n'a pas été déclaré : \"{}\"".format(ident)
		super().__init__(ident.pos, message)

class UnresolvableTypeAlias(MissingDeclaration):
	pass

class FormalParameterMissingInLexicon(SemanticError):
	"""
	Raised when a function's formal parameter was not found in its lexicon.
	"""
	def __init__(self, ident):
		message = ("ce paramètre formel n'a pas été déclaré dans le "
				"lexique de la fonction : \"{}\"").format(ident)
		super().__init__(ident.pos, message)

class DuplicateDeclaration(SemanticError):
	"""
	Raised when an identifier is used in a declaration more than once.
	"""
	def __init__(self, ident, previous_ident):
		message = ("l'identificateur \"{}\" est déjà pris "
				"(déclaration préalable à la position {})").format(
				ident.name, previous_ident.pos)
		super().__init__(ident.pos, message)

class TypeError(SemanticError):
	"""
	Base class for semantic errors pertaining to type problems.

	The constructor takes 1 or more types that are incriminated in the
	problem. If a single one of these is irrelevant, the entire TypeError is
	considered irrelevant. See the docstrings on SemanticError to learn more
	about error relevance.
	"""
	def __init__(self, pos, message, *incriminated_types):
		super().__init__(pos, message)
		assert len(incriminated_types) > 0, \
				"there must be at least one incriminated type!"
		for i in incriminated_types:
			try:
				if not i.relevant_in_semantic_errors:
					self.relevant = False
					break
			except AttributeError:
				pass

class TypeMismatch(TypeError):
	"""
	Raised when two types are expected to be equivalent or identical, and the
	compiler cannot decide which type makes the most sense to use.
	"""
	def __init__(self, pos, what, a, b):
		message = "{} ({} vs. {})".format(what, a, b)
		super().__init__(pos, message, a, b)

class SpecificTypeExpected(TypeError):
	"""
	Raised when an item of a specific type is expected, but an item of another
	type is given.
	"""
	def __init__(self, pos, what, expected, given):
		message = "{} doit être de type {} (et non pas {})".format(
				what, expected, given)
		super().__init__(pos, message, given)

class NonComposite(TypeError):
	"""
	Raised when the user tries to access a member within a non-composite item.
	"""
	def __init__(self, pos, given_type):
		message = ("cet élément n'a aucun membre car il n'est pas de type "
				"composite (il est de type {})").format(given_type)
		super().__init__(pos, message, given_type)

class NonSubscriptable(TypeError):
	"""
	Raised when the user tries to index a non-subscriptable item (i.e. not an
	array).
	"""
	def __init__(self, pos, given_type):
		message = ("cet élément ne peut pas être indicé car il n'est pas de "
				"type tableau (il est de type {})").format(given_type)
		super().__init__(pos, message, given_type)

class NonCallable(TypeError):
	"""
	Raised when the user tries to call a non-callable item (i.e. not a function).
	"""
	def __init__(self, pos, given_type):
		message = ("cet élément ne peut pas être appelé car ce n'est pas une "
				"fonction (il est de type {})").format(given_type)
		super().__init__(pos, message, given_type)

class CountMismatch(SemanticError):
	"""
	Raised when the number of items given does not match that which is expected.

	Typically used with arglists.
	"""
	def __init__(self, pos, expected, given):
		message = "{self_wants} {x} {things}, mais {only}{y} {were_given}".format(
				self_wants = self.self_wants,
				x = expected,
				things = self.singular[0] if expected < 2 else self.plural[0],
				only = "seulement " if given < expected else "",
				y = given,
				were_given = self.singular[1] if given < 2 else self.plural[1])
		super().__init__(pos, message)

class DimensionCountMismatch(CountMismatch):
	self_wants = "ce tableau possède"
	singular = ("dimension", "est fournie")
	plural = ("dimensions", "sont fournies")

class ParameterCountMismatch(CountMismatch):
	self_wants = "cette fonction requiert"
	singular = ("paramètre", "est fourni")
	plural = ("paramètres", "sont fournis")

class RecursiveDeclaration(SemanticError):
	def __init__(self, pos):
		super().__init__(pos, "déclaration récursive")

