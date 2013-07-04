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

class ExpectedError(SyntaxError):
	'''
	Raised when the parser expects an item at a certain position, but encounters
	something else.
	'''

	def __init__(self, pos, expected_keyword):
		message = "'" + expected_keyword[0] + "' est attendu ici"
		SyntaxError.__init__(self, pos, message)

