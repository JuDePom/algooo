"""
Semantic errors that can be raised during the semantic analysis phase.
"""

class SemanticError(Exception):
	"""
	Raised when the semantic analysis on a given element fails.

	This happens when the user writes syntactically correct code which will
	invariably fail to produce a working program.
	"""
	def __init__(self, pos, message):
		self.pos = pos
		message = pos.pretty() + ": erreur de sémantique : " + message
		super().__init__(message)

class MissingDeclaration(SemanticError):
	"""
	Raised when an identifier is used in a statement without having been declared
	in the current context.
	"""
	def __init__(self, ident):
		message = "cet identificateur n'a pas été déclaré : " + str(ident)
		super().__init__(ident.pos, message)

class UnresolvableTypeAlias(MissingDeclaration):
	pass

class FormalParameterMissingInLexicon(SemanticError):
	"""
	Raised when a function's formal parameter was not found in its lexicon.
	"""
	def __init__(self, ident):
		message = ("ce paramètre formel n'a pas été déclaré dans le "
			"lexique de la fonction : ") + str(ident)
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
	"""
	pass

class TypeMismatch(TypeError):
	"""
	Raised when two types are expected to be equivalent or identical, and the
	compiler cannot decide which type makes the most sense to use.
	"""
		super().__init__(pos, message)

class SpecificTypeExpected(TypeError):
	"""
	Raised when an item of a specific type is expected, but an item of another
	type is given.
	"""
	def __init__(self, pos, what, expected, given):
		message = "{} doit être de type {} (et non pas {})".format(
				what, expected, given)
		super().__init__(pos, message)

class NonComposite(SemanticError):
	"""
	Raised when the user tries to access a member within a non-composite item.
	"""
	def __init__(self, pos):
		super().__init__(pos, "cet élément n'a aucun membre car "
			"il n'est pas de type composite")

class NonSubscriptable(SemanticError):
	"""
	Raised when the user tries to index a non-subscriptable item (i.e. not an
	array).
	"""
	def __init__(self, pos):
		super().__init__(pos, "cet élément ne peut pas être indicé car "
			"il n'est pas de type tableau")

class NonCallable(SemanticError):
	"""
	Raised when the user tries to call a non-callable item (i.e. not a function).
	"""
	def __init__(self, pos):
		super().__init__(pos, "cet élément ne peut pas être appelé car "
			"ce n'est pas une fonction")

class CountMismatch(SemanticError):
	"""
	Raised when the number of items given does not match that which is expected.

	Typically used with Varargs.
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

