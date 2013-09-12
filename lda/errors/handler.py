class Logger:
	def __init__(self):
		self.errors = []

	def __bool__(self):
		return bool(self.errors)

	def log(self, error):
		self.errors.append(error)

	@property
	def relevant_errors(self):
		return (e for e in self.errors if e.relevant)

class Raiser:
	def log(self, error):
		raise error

class DummyHandler:
	def log(self, error):
		pass

