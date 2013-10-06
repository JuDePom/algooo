from lda import builtin

class ContextStack:
	class Context:
		def __init__(self, symbols, parent):
			self.symbols = symbols
			self.parent = parent

	def __init__(self, options, symbols=None, parent=None):
		self.options = options
		if symbols is None:
			symbols = builtin.SYMBOLS.copy()
		self.stack = [ContextStack.Context(symbols, parent)]

	def push(self, parent):
		symbols = self.stack[-1].symbols.copy()
		self.stack.append(ContextStack.Context(symbols, parent))

	def pop(self):
		self.stack.pop()

	def __getitem__(self, i):
		return self.stack[-1].symbols[i]

	def __setitem__(self, i, v):
		self.stack[-1].symbols[i] = v

	def update(self, extra_symbol_table):
		self.stack[-1].symbols.update(extra_symbol_table)

	@property
	def parent(self):
		return self.stack[-1].parent

