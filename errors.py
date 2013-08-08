'''
Lexical, syntactic, and semantic errors that can be raised as exceptions during
compilation.
'''

class LDAError(Exception):
	pass

class LDASyntaxError(LDAError):
	'''
	Raised when the parser encounters an LDA syntax errorLDA.
	'''

	def __init__(self, pos, message):
		message = pos.pretty() + ": erreur de syntaxe : " + message
		super().__init__(message)

class ExpectedKeywordError(LDASyntaxError):
	'''
	Raised when the parser expects a keyword at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, *expected_keywords):
		if len(expected_keywords) == 1:
			message = "le mot-clé \"{}\" est attendu ici".format(
					expected_keywords[0].default_spelling)
		else:
			message = "l'un des mot-clés suivants est attendu ici : "
			sep = ""
			for keyword in expected_keywords:
				message += "{}\"{}\"".format(sep, keyword.default_spelling)
				sep = ", "
		super().__init__(pos, message)

class ExpectedItemError(LDASyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, item_name):
		message = item_name + " est attendu(e) ici"
		super().__init__(pos, message)

class IllegalIdentifier(LDASyntaxError):
	'''
	Raised when an identifier was expected but the input doesn't conform to the
	identifier naming format
	'''

	def __init__(self, pos):
		message = "mauvais format d'identifieur"
		super().__init__(pos, message)

class LDASemanticError(LDAError):
	def __init__(self, pos, message):
		message = pos.pretty() + ": erreur de sémantique : " + message
		super().__init__(message)

class MissingDeclaration(LDASemanticError):
	def __init__(self, ident):
		message = "cet identificateur n'a pas été déclaré : " + str(ident)
		super().__init__(ident.pos, message)

class TypeMismatch(LDASemanticError):
	def __init__(self, pos, a, b):
		message = "types conflictuels : {} vs. {}".format(a, b)
		super().__init__(pos, message)

