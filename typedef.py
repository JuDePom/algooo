import keywords as kw
#TODO decide - from tree import SourceThing, Identifier
from tokens import Identifier

class Typedef():
	def __init__(self, type_word, array_dimensions=None):
		synthetic = isinstance(type_word, kw.KeywordDef)
		self.pos = None if synthetic else type_word.pos
		#super().__init__(None if synthetic else type_word.pos)
		self.type_word        = type_word
		self.array_dimensions = array_dimensions
		# useful automatic flags
		self.synthetic        = synthetic
		self.composite        = isinstance(type_word, Identifier)
		self.scalar           = not self.composite
		self.array            = self.array_dimensions is not None
		self.unit             = not self.array
		self.pure_composite   = self.unit and self.composite
		self.pure_scalar      = self.unit and self.scalar
		if self.composite:
			self.composite_name = self.type_word.name

	def make_pure(self):
		return Typedef(self.type_word)

	def __eq__(self, other):
		if isinstance(other, kw.KeywordDef):
			return self.pure_scalar and self.type_word == other
		elif not isinstance(other, Typedef):
			return False
		return self.type_word == other.type_word and \
				self.array_dimensions == other.array_dimensions

	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		s = str(self.type_word)
		if self.array:
			s = "tableau {}{}".format(s, self.array_dimensions)
		return "Typedef/{}".format(s)

INT    = Typedef(kw.INT)
REAL   = Typedef(kw.REAL)
BOOL   = Typedef(kw.BOOL)
STRING = Typedef(kw.STRING)
CHAR   = Typedef(kw.CHAR)

scalars = [ INT, REAL, BOOL, STRING, CHAR ]

