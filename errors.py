'''
Lexical, syntactic, and semantic errors that can be raised as exceptions during
compilation.
'''

class SyntaxError(Exception):
	'''
	Raised when the parser encounters an LDA syntax error.
	'''

	def __init__(self, pos, message):
		message = pos.pretty() + ": erreur de syntaxe: " + message
		Exception.__init__(self, message)

class ExpectedKeywordError(SyntaxError):
	'''
	Raised when the parser expects a keyword at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, expected_keyword):
		message = "'" + expected_keyword.default_spelling + "' est attendu ici"
		SyntaxError.__init__(self, pos, message)

class ExpectedItemError(SyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, item_name):
		message = item_name + " est attendu(e) ici"
		SyntaxError.__init__(self, pos, message)

class IllegalIdentifier(SyntaxError):
	'''
	Raised when an identifier was expected but the input doesn't conform to the
	identifier naming format
	'''

	def __init__(self, pos):
		message = "mauvais format d'identifieur"
		SyntaxError.__init__(self, pos, message)

class UnimplementedError(SyntaxError):
	'''
	Raised when an unimplemented, but legal, feature has been used.
	'''

	def __init__(self, pos, feature_name):
		message = "la fonctionnalité \"" + feature_name + \
				"\" n'a pas encore été implémentée dans le compilateur ! à faire !"
		SyntaxError.__init__(self, pos, message)

