'''
Lexical and syntactic errors that can be raised during the parsing phase.
'''

class SyntaxError(Exception):
	'''
	Raised when the parser encounters an LDA syntax error.
	'''

	def __init__(self, pos, message):
		self.pos = pos
		message = "{} : erreur de syntaxe : {}".format(pos, message)
		super().__init__(message)

class ExpectedItem(SyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, item_name):
		message = item_name + " est attendu(e) ici"
		super().__init__(pos, message)

class ExpectedKeyword(ExpectedItem):
	'''
	Raised when the parser expects a keyword at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, *expected_keywords):
		if len(expected_keywords) == 1:
			message = "mot-clé \"{}\"".format(
					expected_keywords[0].default_spelling)
		else:
			message = "l'un des mot-clés suivants : {}".format(
				", ".join('"{}"'.format(k) for k in expected_keywords))
		super().__init__(pos, message)

class IllegalIdentifier(SyntaxError):
	'''
	Raised when an identifier was expected but the input doesn't conform to the
	identifier naming format.
	'''

	def __init__(self, pos):
		message = "mauvais format d'identifieur"
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

