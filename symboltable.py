class SymbolTable:
	def __init__(self, variables=[], functions=[], molds=[]):
		def makedict(L):
			return dict([(item.ident.name, item) for item in L])
		self.variables = makedict(variables)
		self.functions = makedict(functions)
		self.molds = makedict(molds)
	
	@staticmethod
	def merge(parent, sub):
		table = SymbolTable()
		for k in 'variables', 'functions', 'molds':
			merged = getattr(parent, k).copy()
			merged.update(getattr(sub, k))
			setattr(table, k, merged)
		return table

