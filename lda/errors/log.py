class SemanticErrorLogger:
	def __init__(self):
		self.errors = []

	def __bool__(self):
		return bool(self.errors)

	def log(self, error):
		self.errors.append(error)

class SemanticErrorRaiser:
	def log(self, error):
		raise error

