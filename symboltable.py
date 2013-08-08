from position import SourceThing
from typedef import Typedef

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

class VariableDeclaration(SourceThing):
	def __init__(self, ident, inout, type_word, array_dimensions):
		super().__init__(ident.pos)
		self.ident = ident
		self.inout = inout
		self.typedef = Typedef(type_word, array_dimensions)
	def __repr__(self):
		inout_str = " inout" if self.inout else ""
		return "{}{} : {}".format(self.ident, inout_str, self.typedef)

