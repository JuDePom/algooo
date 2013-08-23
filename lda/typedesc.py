from . import keywords as kw
from .errors import semantic
from types import MethodType

def _hunt_duplicates(item_list):
	seen = {}
	for item in item_list:
		name = item.ident.name
		try:
			pioneer = seen[name]
			raise semantic.DuplicateDeclaration(item.ident, pioneer.ident)
		except KeyError:
			seen[name] = item

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

class ErroneousType(TypeDescriptor):
	def __init__(self, name):
		super().__init__()
		self.name = name

class Scalar(TypeDescriptor):
	def __init__(self, keyword):
		super().__init__()
		self.keyword = keyword

	def __repr__(self):
		return str(self.keyword)

	def __eq__(self, other):
		return self is other

	def check(self, context):
		return self

	def lda_format(self, indent=0):
		return str(self.keyword)

def _dual_scalar_compatibility(weak, strong):
	def weak_equivalent(self, other):
		if other in (weak, strong):
			return other
	def strong_equivalent(self, other):
		if other in (weak, strong):
			return self
	weak.equivalent   = MethodType(weak_equivalent, weak)
	strong.equivalent = MethodType(strong_equivalent, strong)

Integer   = Scalar(kw.INT)
Real      = Scalar(kw.REAL)
Boolean   = Scalar(kw.BOOL)
Character = Scalar(kw.CHAR)
String    = Scalar(kw.STRING)
Void      = Scalar(None)

_dual_scalar_compatibility(weak=Integer, strong=Real)
_dual_scalar_compatibility(weak=Character, strong=String)

class Range(TypeDescriptor):
	pass

class ArrayType(TypeDescriptor):
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

	def check(self, context):
		if len(self.dimensions) == 0:
			raise semantic.SemanticError(self.dimensions.pos,
					"un tableau doit avoir au moins une dimension")
		for dim in self.dimensions:
			dim_type = dim.check(context).resolved_type
			if dim_type is not Range:
				raise semantic.SpecificTypeExpected(
						dim.pos, "une dimension de tableau", Range, dim_type)
		# TODO kludgey
		self.resolved_element_type = self.element_type.check(context).resolved_type
		return self

	def lda_format(self, indent=0):
		return "{kw.ARRAY} {element_type}[{dimensions}]".format(
				kw = kw,
				element_type = self.element_type.lda_format(),
				dimensions = ", ".join(dim.lda_format() for dim in self.dimensions))

	def equivalent(self, other):
		if not isinstance(other, ArrayType):
			return
		if self.element_type != other.element_type:
			return
		if len(self.dimensions) != len(other.dimensions):
			return
		# TODO est-ce qu'on s'occupe des intervalles ?
		return self

class CompositeType(TypeDescriptor):
	def __init__(self, ident, field_list):
		super().__init__()
		self.ident = ident
		self.field_list = field_list

	def __eq__(self, other):
		if self is other:
			return True
		if not isinstance(other, CompositeType):
			return False
		return self.ident == other.ident and self.field_list == other.field_list

	def check(self, supercontext):
		assert not hasattr(self, 'context'), "inutile de redéfinir le contexte"
		_hunt_duplicates(self.field_list)
		self.context = {field.ident.name: field for field in self.field_list}
		for field in self.field_list:
			field.check(supercontext)
		return self

	def detect_loops(self, composite):
		for field in self.field_list:
			if field.resolved_type is composite:
				raise semantic.RecursiveDeclaration(field.ident.pos)
			try:
				field.resolved_type.detect_loops(composite)
			except AttributeError:
				pass

	def lda_format(self, indent=0):
		result = ", ".join(param.lda_format() for param in self.field_list)
		return "<{}>".format(result)

class Identifier:
	def __init__(self, pos, name):
		self.pos = pos
		self.name = name

	def __repr__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return self.name != other.name

	def lda_format(self, indent=0):
		return self.name

	def check(self, context):
		try:
			return context[self.name]
		except KeyError:
			raise semantic.MissingDeclaration(self)

class TypeAlias(Identifier):
	def check(self, context):
		try:
			symbol = context[self.name]
		except KeyError:
			# TODO return ErroneousType ?
			raise semantic.UnresolvableTypeAlias(self)
		if isinstance(symbol, CompositeType):
			return symbol
		else:
			raise semantic.SpecificTypeExpected(self.pos,
					"cet alias", CompositeType, type(symbol))

class Field:
	def __init__(self, ident, type_descriptor):
		self.ident = ident
		self.type_descriptor = type_descriptor

	def __eq__(self, other):
		if self is other:
			return True
		return self.ident == other.ident and self.type_descriptor == other.type_descriptor

	def check(self, context):
		self.resolved_type = self.type_descriptor.check(context).resolved_type
		return self

	def lda_format(self, indent=0):
		return "{} : {}".format(self.ident.name,
				self.type_descriptor.lda_format())

class Lexicon:
	def __init__(self, variables=None, composites=None, functions=None):
		assert(variables  is None or type(variables)  is list)
		assert(composites is None or type(composites) is list)
		assert(functions  is None or type(functions)  is list)
		self.variables  = variables  if variables  is not None else []
		self.composites = composites if composites is not None else []
		self.functions  = functions  if functions  is not None else []
		self.all_items = self.variables + self.composites + self.functions
		self.symbol_dict = {item.ident.name: item for item in self.all_items}
	
	def check(self, supercontext=None):
		# initialize supercontext if needed
		if supercontext is None:
			supercontext = {}
		# hunt duplicates
		_hunt_duplicates(sorted(self.all_items, key = lambda item: item.ident.pos))
		# TODO : optionnellement, avertir si on écrase un nom du scope au-dessus
		# fill subcontext with references to the composites so that they can
		# cross-reference themselves during the next pass
		subcontext = supercontext.copy()
		subcontext.update({c.ident.name: c for c in self.composites})
		subcontext.update({f.ident.name: f for f in self.functions})
		# refine composite subcontexts
		for composite in self.composites:
			composite.check(subcontext)
		# Function pass 1: signatures. Resolve function signatures before function
		# bodies, so that the bodies can refer to other functions.
		for function in self.functions:
			function.check_signature(subcontext)
		# Function pass 2: bodies.
		for function in self.functions:
			function.check(subcontext)
		# do the semantic analysis on the variables last so that they can take
		# advantage of the composites that were defined in this lexicon.
		# Put their resolved types in a separate context so that they can't "borrow"
		# another variable's type by using its name as a TypeAlias.
		# TODO - if there are any global variables this will need to be refined.
		# TODO - they might still be able to borrow function return types from the name of the function...
		variable_context = {v.ident.name: v.type_descriptor.check(subcontext)
				for v in self.variables}
		# merge
		subcontext.update(variable_context)
		return subcontext

	def lda_format(self, indent=0):
		composites = "\n".join("\t{} = {}".format(c.ident.name, c.lda_format())
				for c in sorted(self.composites, key=lambda c: c.ident.name))
		variables = "\n".join("\t" + v.lda_format()
				for v in sorted(self.variables, key=lambda v: v.ident.name))
		if variables == "" and composites == "":
			return ""
		elif variables == "":
			declarations = composites
		elif composites == "":
			declarations = variables
		else:
			declarations = '\n'.join([composites, variables])
		return "{kw.LEXICON}\n{declarations}".format(
				kw = kw,
				declarations = declarations)

