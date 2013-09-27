from .errors import semantic, handler
from . import kw
from . import prettyprinter
from . import semantictools
from .identifier import PureIdentifier
from types import MethodType

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

	def resolve_type(self, context, logger):
		raise NotImplementedError

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

	def js_declare(self, pp):
		"""
		Generate a JavaScript declaration of a variable whose resolved_type is
		this LDA type descriptor.
		"""
		raise NotImplementedError


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

	def resolve_type(self, context, logger):
		return self


"""
The ERRONEOUS black hole type is used whenever an identifier does not refer to
any existing symbol in the symbol table.
"""
ERRONEOUS = BlackHole("<type erronné>")
ERRONEOUS.relevant_in_semantic_errors = False

"""
The NOT_A_VARIABLE black hole type is used whenever an identifier resolves to a
non-variable (anything that is not a VarDecl, such as a function name or a
composite name) in a context where a VarDecl was expected.

For example, in an expression, it is forbidden to perform arithmetic on a
function name without calling it; in that case, the ExpressionIdentifier
representing the function's name will resolve to a NOT_A_VARIABLE type.
"""
NOT_A_VARIABLE = BlackHole("<pas une variable>")


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

	def resolve_type(self, context, logger):
		return self

	def lda(self, pp):
		pp.put(str(self.keyword))

	def js_declare(self, pp):
		pp.put("null")

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
# TYPES THAT NEED TO BE RESOLVED
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

	def resolve_type(self, context, logger):
		self.resolved_core = self.core.resolve_type(context, logger)
		return self.resolved_core

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


class TypeAlias(PureIdentifier, TypeDescriptor):
	"""
	Identifier that can only refer to a Composite.

	It is bound to a Composite during the semantic analysis.
	"""

	def resolve_type(self, context, logger):
		try:
			symbol = context[self.name]
		except KeyError:
			logger.log(semantic.UnresolvableTypeAlias(self))
			self.bound = ERRONEOUS
			return ERRONEOUS
		if isinstance(symbol, Composite):
			self.bound = symbol
			return self.bound
		else:
			logger.log(semantic.SpecificTypeExpected(self.pos,
					"cet alias", Composite, type(symbol)))
			self.bound = ERRONEOUS
			return ERRONEOUS


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
			self.pos = expression.pos
			self.expression = expression

		def __eq__(self, other):
			return self is other or (isinstance(other, Array.StaticDimension) and \
					self.expression == other.expression)

		def check(self, logger):
			"""
			Perform a semantic analysis on the dimension and return True if it
			succeeded.

			Note that no context is passed to this method. This is because the
			expression making up the dimension may not look up variables, since
			it must be evaluable at compile time.
			"""
			# Don't let the expression look up variables.
			# It has to be evaluable at compile time.
			try:
				self.expression.check({}, handler.Raiser())
			except semantic.MissingDeclaration as e:
				logger.log(semantic.SemanticError(e.pos,
						"une borne de tableau statique doit être construite à partir "
						"d'une expression constante"))
				return False
			if self.expression.resolved_type is not RANGE:
				logger.log(semantic.TypeError(self.expression.pos,
						"les bornes d'un tableau statique doivent être données "
						"sous forme d'intervalle d'entiers littéraux",
						self.expression.resolved_type))
				return False
			self.low  = self.expression.lhs
			self.high = self.expression.rhs
			return True

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

		def check(self, logger):
			"""
			Perform a semantic analysis on the dimension and return True if it
			succeeded.
			"""
			return True

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

	def __repr__(self):
		pp = prettyprinter.LDAPrettyPrinter()
		self.lda(pp)
		return str(pp)

	def resolve_type(self, context, logger):
		"""
		Perform a semantic analysis on the dimensions and the element type. Set
		the `resolved_element_type` attribute and the `dynamic` and `static`
		boolean attributes.
		"""
		# Innocent until proven guilty.
		erroneous = False
		# Check dimensions.
		if len(self.dimensions) == 0:
			logger.log(semantic.SemanticError(self.pos,
					"un tableau doit avoir au moins une dimension"))
			erroneous = True
		else:
			dim0_type = type(self.dimensions[0])
			self.dynamic = dim0_type is Array.DynamicDimension
			self.static = not self.dynamic
			for dim in self.dimensions:
				# Semantic analysis of the dimension.
				if not dim.check(logger):
					erroneous = True
				# Ensure we don't have a mix of static and dynamic dimensions.
				if type(dim) is not dim0_type:
					logger.log(semantic.SemanticError(dim.pos,
							"un tableau doit être complètement statique ou "
							"complètement dynamique"))
					erroneous = True
		# Resolve element type.
		self.resolved_element_type = self.element_type.resolve_type(context, logger)
		# If an error occured during this method, the entire type is erroneous.
		return ERRONEOUS if erroneous else self

	def lda(self, pp):
		pp.put(kw.ARRAY, " ", self.element_type, kw.LSBRACK)
		pp.join(self.dimensions, pp.put, ", ")
		pp.put(kw.RSBRACK)

	def js_declare(self, pp):
		# The JS runtime implementation requires LDA arrays to be LDA.Array
		# "objects". We can make such an object right away if the array is
		# static. Otherwise we'll have to wait until the user calls the array
		# allocation builtin function.
		if self.static:
			self.js_new(pp, ((dim.low, dim.high) for dim in self.dimensions))
		else:
			pp.put("null")

	def js_new(self, pp, dimensions):
		"""
		Generate a `new` statement for an LDA.Array. `dimensions` is an
		iterable of ranges; each range is represented by a tuple containing two
		expressions.
		"""
		pp.put("new LDA.Array([")
		prefix = ""
		for dim in dimensions:
			pp.put(prefix, "[", dim[0], ", ", dim[1], "]")
			prefix = ", "
		pp.put("], function(){return ")
		self.resolved_element_type.js_declare(pp)
		pp.put(";})")

	def equivalent(self, other):
		if not isinstance(other, Array):
			return
		if self.element_type != other.element_type:
			return
		if len(self.dimensions) != len(other.dimensions):
			return
		for my_dim, their_dim in zip(self.dimensions, other.dimensions):
			if my_dim != their_dim:
				return
		return self


class Composite(TypeDescriptor):
	"""
	Composite type declaration. Contains an identifier (the name of the
	composite type) and a list of member fields.
	"""

	def __init__(self, ident, fields):
		super().__init__()
		self.ident = ident
		self.fields = fields

	def __eq__(self, other):
		if self is other:
			return True
		if not isinstance(other, Composite):
			return False
		return self.ident == other.ident and self.fields == other.fields

	def __repr__(self):
		return "composite \"{}\"".format(self.ident)

	def resolve_type(self, supercontext, logger):
		"""
		Create `self.context`: a mini-symbol table associating field name
		strings the fields themselves.

		Also hunts down duplicate field names and sets the `parent` attribute.
		"""
		assert not hasattr(self, 'context'), "inutile de redéfinir le contexte"
		self.parent = supercontext.parent
		semantictools.hunt_duplicates(self.fields, logger)
		self.context = {field.ident.name: field for field in self.fields}
		for field in self.fields:
			field.check(supercontext, logger)
		return self

	def detect_loops(self, composite, logger):
		"""
		Log RecursiveDeclaration for every infinite recursion among field type
		descriptors.

		An infinite recursion occurs when a field's type descriptor (or one of
		its children, grandchildren...) refers to the composite type passed to
		this method.
		"""
		for field in self.fields:
			if field.resolved_type is composite:
				logger.log(semantic.RecursiveDeclaration(field.ident.pos))
			try:
				field.resolved_type.detect_loops(composite, logger)
			except AttributeError:
				pass

	def lda(self, pp):
		pp.put(self.ident, " ", kw.EQ, " ", kw.LT)
		pp.join(self.fields, pp.put, ", ")
		pp.put(kw.GT)

	def js(self, pp):
		prefix = getattr(self.parent, 'js_namespace', "var ")
		pp.putline(prefix, self.ident, " = function() {")
		for field in self.fields:
			pp.indented(pp.put, "this.", field.ident, " = ");
			pp.indented(field.resolved_type.js_declare, pp)
			pp.indented(pp.putline, ";")
		pp.put("};")

	def js_declare(self, pp):
		prefix = getattr(self.parent, 'js_namespace', '')
		pp.put("new ", prefix, self.ident, "()")

