"""
Semantic errors that can be raised during the semantic analysis phase.
"""

from .error import LDAError

class SemanticError(LDAError):
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
		super().__init__(pos, message)
		self.relevant = True

class MissingDeclaration(SemanticError):
	"""
	Raised when an identifier is used in a statement without having been declared
	in the current context.
	"""
	def __init__(self, ident, intro="cet identificateur n'a pas été déclaré"):
		message = "{} : \"{}\"".format(intro, ident)
		super().__init__(ident.pos, message)

class UnresolvableTypeAlias(MissingDeclaration):
	def __init__(self, ident):
		super().__init__(ident, "ce type n'existe pas")

class DuplicateDeclaration(SemanticError):
	"""
	Raised when an identifier is used in a declaration more than once.
	"""
	def __init__(self, item, previous_item):
		message = ("l'identificateur \"{}\" est déjà pris "
				"(déclaration préalable à la position {})").format(
				item.name, previous_item.pos)
		super().__init__(item.pos, message)

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
		super().__init__(pos, message, expected, given)

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

class NonWritable(TypeError):
	"""
	Raised when a non-writable expression is used in place of a variable
	identifier.
	"""
	def __init__(self, expression):
		super().__init__(expression.pos,
				"une variable est attendue à la place de cette expression, car "
				"elle doit pouvoir être modifiée (or, le résultat de cette "
				"expression est figé)", getattr(expression, 'resolved_type', None))

class _CountMismatch(SemanticError):
	"""
	Raised when the number of items given does not match that which is expected.
	Typically used with arglists.

	This error class cannot be used as-is. Subclasses must provide the
	following attributes:
	- self_wants: introductory string (such as "this object requires")
	- singular: tuple of two strings. String #0 contains the name of the
	  expected item in singular form. String #1 is the phrase "was given" in
	  singular form.
	- plural: same as singular except that the phrases are in plural form.
	"""
	def __init__(self, pos, expected, given, at_least=False):
		message = "{self_wants} {at_least}{x} {things}, mais {only}{y} {were_given}".format(
				self_wants = self.self_wants,
				at_least = "au moins " if at_least else "",
				x = expected,
				things = self.singular[0] if expected < 2 else self.plural[0],
				only = "seulement " if given < expected else "",
				y = given,
				were_given = self.singular[1] if given < 2 else self.plural[1])
		super().__init__(pos, message)

class DimensionCountMismatch(_CountMismatch):
	self_wants = "ce tableau possède"
	singular = ("dimension", "est fournie")
	plural = ("dimensions", "sont fournies")

class ParameterCountMismatch(_CountMismatch):
	self_wants = "cette fonction requiert"
	singular = ("paramètre", "est fourni")
	plural = ("paramètres", "sont fournis")

class RecursiveDeclaration(SemanticError):
	def __init__(self, pos):
		super().__init__(pos, "déclaration récursive")

class UnreachableStatement(SemanticError):
	def __init__(self, pos):
		super().__init__(pos, "instruction jamais atteinte")

class MissingReturnStatement(SemanticError):
	def __init__(self, pos):
		super().__init__(pos, "il manque une instruction retourne dans "
				"cette fonction")

class UninitializedVariable(SemanticError):
	def __init__(self, pos, decl):
		super().__init__(pos, "\"{}\" : variable non-initialisée".format(decl.name))

class UnusedVariable(SemanticError):
	def __init__(self, decl):
		super().__init__(decl.pos, "\"{}\" : variable non-utilisée".format(decl.name))

