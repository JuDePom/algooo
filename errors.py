class SyntaxError(Exception):
	def __init__(self, pos, message):
		message = pos.pretty() + ": erreur de syntaxe: " + message
		Exception.__init__(self, message)

class ExpectedError(SyntaxError):
	def __init__(self, pos, expected_keyword):
		message = "'" + expected_keyword[0] + "' est attendu ici"
		SyntaxError.__init__(self, pos, message)

