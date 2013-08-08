import keywords as kw
from position import SourceThing
from errors import MissingDeclaration

class Typedef(SourceThing):
	def __init__(self, type_word, array_dimensions=None):
		synthetic = isinstance(type_word, kw.KeywordDef)
		#pos = None if synthetic else type_word.pos
		super().__init__(None if synthetic else type_word.pos)
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

class SymbolTable:
	def __init__(self, variables=[], functions=[], composites=[]):
		def makedict(L):
			return dict([(item.ident.name, item) for item in L])
		self.variables = makedict(variables)
		self.functions = makedict(functions)
		self.composites = makedict(composites)

	@staticmethod
	def merge(parent, sub):
		table = SymbolTable()
		for k in 'variables', 'functions', 'composites':
			merged = getattr(parent, k).copy()
			merged.update(getattr(sub, k))
			setattr(table, k, merged)
		return table

class Lexicon(SourceThing, SymbolTable):
	def __init__(self, pos, variables, composites):
		SourceThing.__init__(self, pos)
		SymbolTable.__init__(self, variables=variables, composites=composites)
	def __repr__(self):
		return "vars = {}\ncomps = {}".format(self.variables, self.composites)

class Composite(SourceThing, SymbolTable):
	def __init__(self, ident, fp_list):
		SourceThing.__init__(self, ident.pos)
		SymbolTable.__init__(self, variables=fp_list)
		self.ident = ident
	def __repr__(self):
		return "{}={}".format(self.ident, self.variables)

class Identifier(SourceThing):
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

class VariableDeclaration(SourceThing):
	def __init__(self, ident, inout, type_word, array_dimensions):
		super().__init__(ident.pos)
		self.ident = ident
		self.inout = inout
		self.typedef = Typedef(type_word, array_dimensions)
	def __repr__(self):
		inout_str = " inout" if self.inout else ""
		return "{}{} : {}".format(self.ident, inout_str, self.typedef)


scalars = {
		'INT': Typedef(kw.INT),
		'REAL': Typedef(kw.REAL),
		'BOOL': Typedef(kw.BOOL),
		'STRING': Typedef(kw.STRING),
		'CHAR': Typedef(kw.CHAR),
}

