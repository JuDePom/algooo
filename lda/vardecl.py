from . import kw
from .types import ERRONEOUS
from .errors import semantic

class VarDecl:
	"""
	Variable declaration.

	Attributes set at parse time:
	- ident
	- type_descriptor
	- formal: flag indicating whether this VarDecl is a formal parameter
	- inout: flag indicating whether this VarDecl is `inout`. Semantically,
	  only formal parameters may be inout.

	Attributes set at semantic time (see check()):
	- resolved_type
	- parent
	- js_fakeptr
	- js_fakepbc

	All variables are writable by default, i.e. they can legally occupy the
	lefthand side of an assignment statement.
	"""

	def __init__(self, ident, type_descriptor, formal, inout):
		self.ident = ident
		self.type_descriptor = type_descriptor
		self.formal = formal
		self.inout = inout

	def __eq__(self, other):
		if self is other:
			return True
		return isinstance(other, VarDecl) and \
				self.ident == other.ident and \
				self.type_descriptor == other.type_descriptor

	def check(self, context, logger):
		"""
		Semantic analysis. Create the following attributes:

		- resolved_type

		- parent: parent algorithm/function/module, will be used to put the
		  variable in the correct JavaScript "namespace"

		- js_fakeptr: in JS, whether references to this variable will go
		  through a fake pointer (implemented with `LDA.ptr()` in the JS
		  runtime). If so, the JS representation of its identifier will be
		  prepended with `ptr`.

		- js_fakepbc: in JS, whether passing this variable around will require
		  faking pass-by-copy (implemented with `LDA.clone()` in the JS
		  runtime).
		"""
		if not self.formal and self.inout:
			logger.log(semantic.SemanticError(self.ident.pos,
					"\"inout\" n'est autorisé que dans un paramètre formel"))
			self.resolved_type = ERRONEOUS
			return
		self.resolved_type = self.type_descriptor.resolve_type(context, logger)
		self.parent = context.parent
		self.js_fakeptr = self.inout and not self.resolved_type.js_object
		self.js_fakepbc = not self.inout and self.resolved_type.js_object

	def lda(self, pp):
		pp.put(self.ident, kw.COLON, " ")
		if self.inout:
			pp.put(kw.INOUT, " ")
		pp.put(self.type_descriptor)

	def js_ident(self, pp, access):
		"""
		Generate JS identifier for this variable.
		`access` must be True if the variable's value is being accessed.
		"""
		prefix = getattr(self.parent, 'js_namespace', '')
		pp.put(prefix)
		if self.js_fakeptr:
			pp.put("ptr")
		pp.put(self.ident)
		if access and self.js_fakeptr:
			pp.put(".v")

