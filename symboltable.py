import keywords as kw
from position import SourceThing
from errors import MissingDeclaration
import dot

scalars = {}
equivalent_scalars = []

class Typedef(SourceThing):
	# TODO documenter que c'est assez statique, c'est-à-dire que
	# si c'est un composite, ça ne prend en compte que le nom du composite
	# et pas le composite en lui-même
	# Ça devrait peut être s'appeler TypeAlias plus exactement ?
	def __init__(self, type_word, array_dimensions=None, inout=False):
		synthetic = isinstance(type_word, kw.KeywordDef)
		#pos = None if synthetic else type_word.pos
		super().__init__(None if synthetic else type_word.pos)
		self.type_word        = type_word
		self.array_dimensions = array_dimensions
		self.inout            = inout
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

	def equivalent(self, other):
		if self == other:
			return True
		return self in equivalent_scalars and other in equivalent_scalars

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
		if self.inout:
			s = "inout " + s
		return "Typedef/{}".format(s)

class SymbolTable:
	def __init__(self, variables=None, functions=None, composites=None):
		def makedict(L):
			return dict([(item.ident.name, item) for item in L])
		if variables is None: variables = []
		if functions is None: functions = []
		if composites is None: composites = []
		# TODO do we really need three distinct lists of symbols?
		# TODO do we even need this to be its own class? couldn't it be a good ole dict?
		self.variables = makedict(variables)
		self.functions = makedict(functions)
		self.composites = makedict(composites)
		self.symbols = {}
		self.symbols.update(self.functions) #functions before composites
		self.symbols.update(self.composites) #composites before variables
		self.symbols.update(self.variables)

	@staticmethod
	def merge(parent, sub):
		table = SymbolTable()
		for k in 'variables', 'functions', 'composites', 'symbols':
			merged = getattr(parent, k).copy()
			merged.update(getattr(sub, k))
			setattr(table, k, merged)
		return table

	def get(self, ident):
		# TODO peut-être faire hériter le hash de Identifier de son name
		return self.symbols[ident.name]


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
		self.typedef = Typedef(ident) # TODO is this really needed?
		# TODO couldn't Composite just be a subclass of Typedef? would make more sense too

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
			#return context.variables[self.name].typedef
			# TODO - uh, excuse me? typedef?
			return context.get(self)
		except KeyError:
			# TODO - peut-être qu'il serait plus judicieux de logger les erreurs
			# sémantiques que de les lever comme exceptions
			raise MissingDeclaration(self)

class VariableDeclaration(SourceThing):
	def __init__(self, ident, typedef):
		super().__init__(ident.pos)
		self.ident = ident
		self.typedef = typedef

	def __repr__(self):
		return "{} : {}".format(self.ident, self.typedef)

	def check(self, context):
		# TODO - vérifier si le type est bon
		# (peut-on le résolver si c'est un composite ?)
		return self.typedef


scalars = {
		'INT': Typedef(kw.INT),
		'REAL': Typedef(kw.REAL),
		'BOOL': Typedef(kw.BOOL),
		'STRING': Typedef(kw.STRING),
		'CHAR': Typedef(kw.CHAR),
}

equivalent_scalars = [
		scalars['INT'],
		scalars['REAL']
]

