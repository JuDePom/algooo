'''
Lexical, syntactic, and semantic errors that can be raised as exceptions during
compilation.
'''

class LDASyntaxError(Exception):
	'''
	Raised when the parser encounters an LDA syntax errorLDA.
	'''

	def __init__(self, pos, message):
		message = pos.pretty() + ": erreur de syntaxe: " + message
		Exception.__init__(self, message)

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
		LDASyntaxError.__init__(self, pos, message)

class ExpectedItemError(LDASyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, item_name):
		message = item_name + " est attendu(e) ici"
		LDASyntaxError.__init__(self, pos, message)

class IllegalIdentifier(LDASyntaxError):
	'''
	Raised when an identifier was expected but the input doesn't conform to the
	identifier naming format
	'''

	def __init__(self, pos):
		message = "mauvais format d'identifieur"
		LDASyntaxError.__init__(self, pos, message)

class UnimplementedError(LDASyntaxError):
	'''
	Raised when an unimplemented, but legal, feature has been used.
	'''

	def __init__(self, pos, feature_name):
		message = "la fonctionnalité \"" + feature_name + \
				"\" n'a pas encore été implémentée dans le compilateur ! à faire !"
		LDASyntaxError.__init__(self, pos, message)

