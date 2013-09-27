class PureIdentifier:
	"""
	User-defined name that identifies an LDA code object.
	"""

	def __init__(self, pos, name):
		self.pos = pos
		self.name = name

	def __repr__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return self.name != other.name

	def lda(self, pp):
		pp.put(self.name)

	def js(self, pp):
		pp.put("$" + self.name)

