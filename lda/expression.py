from . import kw
from . import types
from .identifier import PureIdentifier
from .errors import semantic
from .vardecl import VarDecl

ESCAPE_SEQUENCES = {
	'\\n': '\n',
	'\\t': '\t',
	'\\"': '"',
	"\\'": "'",
	'\\\\': '\\',
}

REVERSE_ESCAPE_SEQUENCES = {v: k for k, v in ESCAPE_SEQUENCES.items()}

def lda_escape_string(s):
	return ''.join(REVERSE_ESCAPE_SEQUENCES.get(c, c) for c in s)

def js_escape_string(s, js_quote):
	# unicode-escape happens to be compatible with JS too
	return s.encode('unicode-escape').decode().replace(js_quote, '\\'+js_quote)

def surround(lda_method):
	"""
	Surround the exported LDA code with parentheses if the object is not the
	root node of an expression.

	Meant to be used as a decorator for `lda` methods in Expression subclasses.
	"""
	def wrapper(self, pp):
		if self.root:
			lda_method(self, pp)
		else:
			pp.put("(")
			lda_method(self, pp)
			pp.put(")")
	return wrapper

def nonwritable(check_method):
	"""
	Surround a semantic check method to automatically log a NonWritable error
	if the access mode is 'w'.
	"""
	def wrapper(self, context, logger, mode='r'):
		if mode != 'r':
			logger.log(semantic.NonWritable(self))
			self.resolved_type = types.ERRONEOUS
		else:
			check_method(self, context, logger)
	return wrapper

class Expression:
	"""
	Base class for all expressions.

	An expression requires the following attributes to be set as soon as
	possible after being created:

	- pos: the expression's position in the input program

	- root: True if the expression is not contained by any other
	  expression. This is set to False by the default constructor.

	- terminal: True if the expression is a terminal symbol.

	In addition, an expression must be checked for semantic correctness with
	the `check()` method. If the semantic analysis is successful, the
	expression gains the `resolved_type` attribute. Otherwise, `resolved_type`
	is set to a `BlackHole` type (typically `ERRONEOUS`).
	"""

	def __init__(self, pos):
		self.pos = pos
		self.root = False
		assert hasattr(self, 'terminal')

	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

	def check(self, context, logger, mode='r'):
		"""
		Check for semantic aberrations and set the resolved_type attribute.

		`mode` indicates how this expression is being accessed. It can be:
		- 'r': read access.
		- 'w': write access.
		- 's': special write-ish access. (inout effective param, memory allocation)
		"""
		raise NotImplementedError


class ExpressionIdentifier(PureIdentifier, Expression):
	"""
	Name bound to a symbol during the semantic analysis phase.
	"""

	terminal = True

	def check(self, context, logger, mode='r'):
		"""
		Resolve the name in the current context's symbol table.

		The `bound` attribute is set to the object referred to by the name.

		The `resolved_type` attribute is set to:
		- `ERRONEOUS` if the name is absent from the symbol table;
		- `NOT_A_VARIABLE` if the name refers to a non-variable object such as
		a composite or a function.
		"""
		# Find corresponding symbol in the context's symbol table.
		try:
			self.bound = context[self.name]
		except KeyError:
			# Make the name refer to a fake symbol (None) so that later
			# invocations of this this name don't raise MissingDeclaration.
			context[self.name] = None
			self.bound = None
			logger.log(semantic.MissingDeclaration(self))
		if self.bound is None or self.bound is types.ERRONEOUS:
			# Bound to an undeclared symbol.
			self.resolved_type = types.ERRONEOUS
			return
		# Steal the bound symbol's type.
		try:
			self.resolved_type = self.bound.resolved_type
		except AttributeError:
			# In the symbol table, only VarDecl objects have a resolved_type
			# attribute. Anything else (function names, composite names) yields
			# a NOT_A_VARIABLE type, which will ultimately trigger a TypeError
			# if this identifier is used improperly.
			self.resolved_type = types.NOT_A_VARIABLE
		# Check bound symbol's writability.
		if isinstance(self.bound, VarDecl):
			self.bound.access(context, logger, self.pos, mode)
		elif mode != 'r':
			logger.log(semantic.NonWritable(self))
			self.resolved_type = types.ERRONEOUS
			return

	def js(self, pp):
		self.bound.js_ident(pp, access=True)


class Literal(Expression):
	"""
	Value hard-coded into the program.
	Not writable.
	"""

	terminal = True

	def __init__(self, pos, value):
		super().__init__(pos)
		self.value = value
		assert hasattr(self, 'resolved_type'), "a literal's resolved_type must be fixed at compile time!"

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value

	def __repr__(self):
		return "littéral {}".format(self.resolved_type)

	@nonwritable
	def check(self, context, logger):
		pass

class LiteralInteger(Literal):
	resolved_type = types.INTEGER

	def lda(self, pp):
		pp.put(str(self.value))
	
	def js(self, pp):
		pp.put(str(self.value))

class LiteralReal(Literal):
	resolved_type = types.REAL

	def lda(self, pp):
		pp.put(str(self.value))
		
	def js(self, pp):
		pp.put(str(self.value))

class LiteralString(Literal):
	resolved_type = types.STRING

	def lda(self, pp):
		pp.put(kw.QUOTE2, lda_escape_string(self.value), kw.QUOTE2)
	
	def js(self, pp):
		pp.put('"', js_escape_string(self.value, '"'), '"')

class LiteralCharacter(Literal):
	resolved_type = types.CHARACTER

	def __init__(self, pos, value):
		super().__init__(pos, value)
		assert len(value) == 1

	def lda(self, pp):
		pp.put(kw.QUOTE1, lda_escape_string(self.value), kw.QUOTE1)

	def js(self, pp):
		pp.put("'", js_escape_string(self.value, "'"), "'")

class LiteralBoolean(Literal):
	resolved_type = types.BOOLEAN

	def lda(self, pp):
		pp.put(kw.TRUE if self.value else kw.FALSE)
		
	def js(self, pp):
		pp.put("true" if self.value else "false")

