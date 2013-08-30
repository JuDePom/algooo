from .errors import semantic, handler
from . import kw
from types import MethodType

#######################################################################
#
# BASE TYPE CLASSES
#
#######################################################################

class TypeDescriptor:
	def __init__(self):
		self.resolved_type = self

	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

	def equivalent(self, other):
		if self.__eq__(other):
			return self

	def compatible(self, other):
		return self.__eq__(other.equivalent(self))

class BlackHole(TypeDescriptor):
	def __eq__(self, other):
		return False

ERRONEOUS = BlackHole()
ERRONEOUS.relevant = False

ASSIGNMENT = BlackHole()


#######################################################################
#
# SCALAR TYPES
#
#######################################################################

class Scalar(TypeDescriptor):
	def __init__(self, keyword, name=None):
		super().__init__()
		self.keyword = keyword
		if name is None:
			self.name = str(self.keyword)
		else:
			self.name = name

	def __repr__(self):
		return self.name

	def __eq__(self, other):
		return self is other

	def check(self, context, logger):
		return self

	def lda(self, exp):
		exp.put(str(self.keyword))

def _dual_scalar_compatibility(weak, strong):
	def weak_equivalent(self, other):
		if other in (weak, strong):
			return other
	def strong_equivalent(self, other):
		if other in (weak, strong):
			return self
	weak.equivalent   = MethodType(weak_equivalent, weak)
	strong.equivalent = MethodType(strong_equivalent, strong)

INTEGER   = Scalar(kw.INT)
REAL      = Scalar(kw.REAL)
BOOLEAN   = Scalar(kw.BOOL)
CHARACTER = Scalar(kw.CHAR)
STRING    = Scalar(kw.STRING)
VOID      = Scalar(None, "<vide>")
RANGE     = Scalar(None, "<intervalle>")

_dual_scalar_compatibility(weak=INTEGER,   strong=REAL)
_dual_scalar_compatibility(weak=CHARACTER, strong=STRING)


#######################################################################
#
# ARRAY TYPE
#
#######################################################################

class Array(TypeDescriptor):
	class StaticDimension:
		def __init__(self, expression):
			self.expression = expression

		def __eq__(self, other):
			return self is other or (isinstance(other, Array.StaticDimension) and \
					self.expression == other.expression)#self.low == other.low and self.high == other.high)

		def check(self, context, logger):
			# Don't let the expression look up variables.
			# It has to be evaluable at compile time.
			try:
				self.expression.check({}, handler.Raiser())
			except semantic.MissingDeclaration as e:
				logger.log(semantic.SemanticError(e.pos,
						"une borne de tableau statique doit être construite à partir "
						"d'une expression constante"))
			if self.expression.resolved_type is not RANGE:
				logger.log(semantic.SemanticError(self.expression.pos,
						"les bornes d'un tableau statique doivent être données "
						"sous forme d'intervalle d'entiers littéraux"))
			self.low  = self.expression.lhs
			self.high = self.expression.rhs

		def lda(self, exp):
			exp.put(self.expression)

	class DynamicDimension:
		def __init__(self, pos):
			self.pos = pos

		def __eq__(self, other):
			return isinstance(other, Array.DynamicDimension)

		def check(self, context, logger):
			pass

		def lda(self):
			exp.put(kw.QUESTION_MARK)

	def __init__(self, element_type, dimensions):
		super().__init__()
		self.element_type = element_type
		self.dimensions = dimensions

	def __eq__(self, other):
		if self is other:
			return True
		if not self.equivalent(other):
			return False
		return self.dimensions == other.dimensions

	def check(self, context, logger):
		if len(self.dimensions) == 0:
			logger.log(semantic.SemanticError(self.dimensions.pos,
					"un tableau doit avoir au moins une dimension"))
		for dim in self.dimensions:
			dim.check(context, logger)
		self.resolved_element_type = self.element_type.check(context, logger).resolved_type
		return self

	def lda(self, exp):
		exp.put(kw.ARRAY, " ", self.element_type, kw.LSBRACK)
		exp.join(self.dimensions, exp.put, ", ")
		exp.put(kw.RSBRACK)

	def equivalent(self, other):
		if not isinstance(other, Array):
			return
		if self.element_type != other.element_type:
			return
		if len(self.dimensions) != len(other.dimensions):
			return
		# TODO est-ce qu'on s'occupe des intervalles ?
		return self


#######################################################################
#
# COMPOSITE TYPE
#
#######################################################################

class Composite(TypeDescriptor):
	def __init__(self, ident, field_list):
		super().__init__()
		self.ident = ident
		self.field_list = field_list

	def __eq__(self, other):
		if self is other:
			return True
		if not isinstance(other, Composite):
			return False
		return self.ident == other.ident and self.field_list == other.field_list

	def check(self, supercontext, logger):
		assert not hasattr(self, 'context'), "inutile de redéfinir le contexte"
		# TODO very ugly import
		from lda.symbols import hunt_duplicates
		hunt_duplicates(self.field_list, logger)
		self.context = {field.ident.name: field for field in self.field_list}
		for field in self.field_list:
			field.check(supercontext, logger)
		return self

	def detect_loops(self, composite, logger):
		for field in self.field_list:
			if field.resolved_type is composite:
				logger.log(semantic.RecursiveDeclaration(field.ident.pos))
			try:
				field.resolved_type.detect_loops(composite, logger)
			except AttributeError:
				pass

	def lda(self, exp):
		exp.put(self.ident, " ", kw.EQ, " ", kw.LT)
		exp.join(self.field_list, exp.put, ", ")
		exp.put(kw.GT)

