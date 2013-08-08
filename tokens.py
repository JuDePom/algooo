import position
import dot
from errors import MissingDeclaration

class Token(position.SourceThing):
	pass

class KeywordToken(Token):
	def __init__(self, pos, kw_def):
		super().__init__(pos)
		self.kw_def = kw_def
	def __eq__(self, other):
		return kw.meta.keyword_equality(self, other)
	def __ne__(self, other):
		return not self.__eq__(other)

class Identifier(Token):
	def __init__(self, pos, name):
		super().__init__(pos)
		self.name = name
	def __eq__(self, other):
		return isinstance(other, Identifier) and self.name == other.name
	def __repr__(self):
		return self.name
	def put_node(self, cluster):
		return dot.Node(str(self), cluster)
	def check(self, context):
		try:
			self.typedef = context.variables[self.name].typedef
		except KeyError:
			# TODO - peut-être qu'il serait plus judicieux de logger les erreurs
			# sémantiques que de les lever comme exceptions
			raise MissingDeclaration(self)

