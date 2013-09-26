from . import kw
from .types import Inout
from .errors import semantic

class VarDecl:
	"""
	Variable declaration. Has an identifier, a type_descriptor and a formal
	flag (i.e. formal parameter).

	Semantically, only formal variables may have the Inout type.

	All variables are writable by default, i.e. they can legally occupy the
	lefthand side of an assignment statement.
	"""

	writable = True

	def __init__(self, ident, type_descriptor, formal=False):
		self.ident = ident
		self.type_descriptor = type_descriptor
		self.formal = formal

	def __eq__(self, other):
		if self is other:
			return True
		return self.ident == other.ident and \
				self.type_descriptor == other.type_descriptor

	def check(self, context, logger):
		if not self.formal and isinstance(self.type_descriptor, Inout):
			logger.log(semantic.SemanticError(self.ident.pos,
					"\"inout\" n'est autorisé que dans un paramètre formel"))
		self.resolved_type = self.type_descriptor.resolve_type(context, logger)

	def lda(self, pp):
		pp.put(self.ident, kw.COLON, " ", self.type_descriptor)

	def js(self, pp):
		if not self.formal:
			self.resolved_type.js_declare(pp, self)

