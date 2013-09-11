from .errors import semantic, handler
from . import kw
from types import MethodType

#######################################################################
#
# UTILITY FUNCTIONS
#
#######################################################################

def _enforce(name, expected_type, typed_object, logger, cmpfunc):
	if typed_object is None:
		given_type = VOID
	else:
		given_type = typed_object.resolved_type
	if cmpfunc(given_type):
		return True
	else:
		logger.log(semantic.SpecificTypeExpected(
			typed_object.pos,
			name,
			expected = expected_type,
			given = given_type))
		return False

def enforce(name, expected_type, typed_object, logger):
	"""
	Ensure the expected type is *equal* to an object's resolved_type.
	Log SpecificTypeExpected if the type does not conform.
	:param expected_type: type the object's resolved type must be equal to
	:param typed_object: object whose resolved_type member will be tested against
			expected_type
	:param logger: semantic error logger
	"""
	return _enforce(name, expected_type, typed_object, logger,
			expected_type.__eq__)

def enforce_compatible(name, expected_type, typed_object, logger):
	"""
	Ensure the expected type is *compatible with* an object's resolved_type.
	Log SpecificTypeExpected if the type does not conform.
	:param expected_type: type the object's resolved type must be equal to
	:param typed_object: object whose resolved_type member will be tested against
			expected_type
	:param logger: semantic error logger
	"""
	return _enforce(name, expected_type, typed_object, logger,
			expected_type.compatible)

#######################################################################
#
# BASE TYPE DESCRIPTOR CLASS
#
#######################################################################

class TypeDescriptor:
	"""
	Base class for all type descriptors.

	Type descriptors may need to be refined through semantic analysis (via the
	check() method) to be complete.
	"""

	def __eq__(self, other):
		raise NotImplementedError

	def __ne__(self, other):
		return not self.__eq__(other)

	def equivalent(self, other):
		"""
		If both types are equivalent, return the 'strongest' type among them;
		else return None. The strongest type will dictate the type of e.g.
		arithmetic expressions.

		Note: any non-blackhole type is equivalent to itself.
		"""
		if self.__eq__(other):
			return self

	def compatible(self, other):
		"""
		Return True if both types are equivalent and this type is the strongest
		of both.
		"""
		return self.__eq__(other.equivalent(self))


#######################################################################
#
# BLACK HOLE TYPES
#
#######################################################################

class BlackHole(TypeDescriptor):
	"""
	Special type that is not equal, equivalent, or compatible with any type
	(not even other BlackHole types).

	BlackHole types cannot be defined directly in the compiled source code.
	They typically occur when the type of an item cannot be resolved, or when
	an expression doesn't have a type.
	"""

	def __init__(self, human_name):
		self.human_name = human_name

	def __eq__(self, other):
		return False

	def __repr__(self):
		return self.human_name


ERRONEOUS = BlackHole("<type erronné>")
ERRONEOUS.relevant = False

NOT_A_VARIABLE = BlackHole("<pas une variable>")
NOT_A_VARIABLE.relevant = True


#######################################################################
#
# SCALAR TYPES
#
#######################################################################

class Scalar(TypeDescriptor):
	"""
	Scalar type.

	Scalar types are meant to be compared using Python's 'is' operator. As
	such, the Scalar class is not meant to be instantiated (besides the
	pre-defined Scalar instances in this module: INTEGER, REAL, etc.).
	"""

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
		pass

	def lda(self, pp):
		pp.put(str(self.keyword))

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
# INOUT WRAPPER
#
#######################################################################

class Inout(TypeDescriptor):
	"""
	Inout wrapper around a core type.
	"""

	def __init__(self, core):
		super().__init__()
		self.core = core

	def __repr__(self):
		return "inout {}".format(self.core)

	def __eq__(self, other):
		return isinstance(other, Inout) and self.core.__eq__(other.core)

	def check(self, context, logger):
		self.core.check(context, logger)

	def equivalent(self, other):
		if isinstance(other, Inout):
			return self.core.equivalent(other.core)
		else:
			return self.core.equivalent(other)

	def compatible(self, other):
		if isinstance(other, Inout):
			return self.core.compatible(other.core)
		else:
			return self.core.compatible(other)


#######################################################################
#
# ARRAY TYPE
#
#######################################################################

class Array(TypeDescriptor):
	"""
	Array type declaration. The array must contain at least one dimension. Each
	dimension can be static or dynamic.
	"""

	class StaticDimension:
		"""
		Created from a constant integer range that must be evaluable at compile
		time.
		"""

		def __init__(self, expression):
			self.expression = expression

		def __eq__(self, other):
			return self is other or (isinstance(other, Array.StaticDimension) and \
					self.expression == other.expression)

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

		def lda(self, pp):
			pp.put(self.expression)

	class DynamicDimension:
		"""
		Created from the '?' keyword.
		"""

		def __init__(self, pos):
			self.pos = pos

		def __eq__(self, other):
			return isinstance(other, Array.DynamicDimension)

		def check(self, context, logger):
			pass

		def lda(self, pp):
			pp.put(kw.QUESTION_MARK)

	def __init__(self, pos, element_type, dimensions):
		super().__init__()
		self.pos = pos
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
			logger.log(semantic.SemanticError(self.pos,
					"un tableau doit avoir au moins une dimension"))
		for dim in self.dimensions:
			dim.check(context, logger)
		self.element_type.check(context, logger)

	def lda(self, pp):
		pp.put(kw.ARRAY, " ", self.element_type, kw.LSBRACK)
		pp.join(self.dimensions, pp.put, ", ")
		pp.put(kw.RSBRACK)

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
	"""
	Composite type declaration. Contains an identifier (the name of the
	composite type) and a list of member fields.
	"""

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

	def __repr__(self):
		return "composite \"{}\"".format(self.ident)

	def check(self, supercontext, logger):
		"""
		Creates self.context: a mini-symbol table associating field name
		strings the fields themselves.

		Also hunts down duplicate field names.
		"""
		assert not hasattr(self, 'context'), "inutile de redéfinir le contexte"
		# TODO very ugly import
		from lda.symbols import hunt_duplicates
		hunt_duplicates(self.field_list, logger)
		self.context = {field.ident.name: field for field in self.field_list}
		for field in self.field_list:
			field.check(supercontext, logger)

	def detect_loops(self, composite, logger):
		"""
		Log RecursiveDeclaration for every infinite recursion among field type
		descriptors.

		An infinite recursion occurs when a field's type descriptor (or one of
		its children, grandchildren...) refers to the composite type passed to
		this method.
		"""
		for field in self.field_list:
			if field.resolved_type is composite:
				logger.log(semantic.RecursiveDeclaration(field.ident.pos))
			try:
				field.resolved_type.detect_loops(composite, logger)
			except AttributeError:
				pass

	def lda(self, pp):
		pp.put(self.ident, " ", kw.EQ, " ", kw.LT)
		pp.join(self.field_list, pp.put, ", ")
		pp.put(kw.GT)

	def js(self, pp):
		pp.putline("var ", self.ident, " = {")
		for field in self.field_list:
			pp.indented(pp.putline, field.ident, ",")
		pp.put("};")

