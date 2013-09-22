'''
Lexical and syntactic errors that can be raised during the parsing phase.
'''

from .error import LDAError

class SyntaxError(LDAError):
	'''
	Raised when the parser encounters an LDA syntax error.
	'''

	def __init__(self, pos, message):
		super().__init__(pos, message)

class ExpectedItem(SyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, item_name, found_instead=None):
		message = item_name + " est attendu(e) ici"
		if found_instead:
			message = "{}, mais \"{}\" a été trouvé à la place".format(message, found_instead)
		super().__init__(pos, message)

class ExpectedKeyword(ExpectedItem):
	'''
	Raised when the parser expects a keyword at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, *expected_keywords, found_instead=None):
		self.expected_keywords = expected_keywords
		if len(expected_keywords) == 1:
			message = "mot-clé \"{}\"".format(
					expected_keywords[0].default_spelling)
		else:
			message = "l'un des mot-clés suivants : {}".format(
				", ".join('"{}"'.format(k) for k in expected_keywords))
		super().__init__(pos, message, found_instead)

class IllegalIdentifier(SyntaxError):
	'''
	Raised when an identifier was expected but the input doesn't conform to the
	identifier naming format.
	'''

	def __init__(self, pos):
		message = "mauvais format d'identificateur"
		super().__init__(pos, message)

class ReservedWord(SyntaxError):
	'''
	Raised when the user tries to use a reserved keyword for an identifier.
	'''

	def __init__(self, pos, word):
		message = "\"{}\" est un mot réservé par le langage".format(word)
		super().__init__(pos, message)

class MissingRightOperand(SyntaxError):
	'''
	Raised when a unary or binary operator is missing its right operand.
	'''

	def __init__(self, pos):
		super().__init__(pos, "cet opérateur requiert un opérande "
			"valide à sa droite")

class DiscardedExpression(SyntaxError):
	'''
	Raised when the result of an expression is discarded.
	'''

	def __init__(self, expr):
		if expr.compound:
			super().__init__(expr.pos, "le résultat de cette expression n'est pas "
					"conservé (peut-être devriez-vous l'affecter à une variable ?)")
		else:
			super().__init__(expr.pos, "lexème errant")

