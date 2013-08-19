from . import keywords as kw
from .errors import semantic
from types import MethodType

class TypeDescriptor:
	pass
		
class ErroneousType(TypeDescriptor):
	def __init__(self, name):
		self.name = name

class Scalar(TypeDescriptor):
	def __init__(self, keyword):
		self.keyword = keyword

	def check(self, context):
		return self

	def equivalent(self, other):
		if other is self:
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

_dual_scalar_compatibility(weak=Integer, strong=Real)
_dual_scalar_compatibility(weak=Character, strong=String)

class Void(TypeDescriptor):
	@staticmethod
	def check(context):
		return Void

class Range(TypeDescriptor):
	pass

class ArrayType(TypeDescriptor):
	def __init__(self, element_type, dimensions):
		self.element_type = element_type
		self.dimensions = dimensions

	def check(self, context):
		if len(self.dimensions) == 0:
			raise semantic.SemanticError(self.dimensions.pos,
					"un tableau doit avoir au moins une dimension")
		for dim in self.dimensions:
			dim_type = dim.check(context)
		# TODO kludgey
		self.resolved_element_type = self.element_type.check(context)
		return self

	def lda_format(self, indent=0):
		return "{kw.ARRAY} {element_type}[{dimensions}]".format(
				kw = kw,
				element_type = self.element_type.lda_format(),
				dimensions = ", ".join(dim.lda_format() for dim in self.dimensions))

class CompositeType(TypeDescriptor):
	def __init__(self, ident, field_list):
		self.ident = ident
		self.name = ident.name
		self.field_list = field_list

	def check_duplicate_fields(self):
		pioneers = {}
		for f in self.field_list:
			try:
				pioneer = pioneers[f.name]
				raise semantic.DuplicateDeclaration(f, pioneer)
			except KeyError:
				pioneers[f.name] = f

	def check(self, supercontext):
		assert not hasattr(self, 'context'), "inutile de redéfinir le contexte"
		self.check_duplicate_fields()
		# add to context
		self.context = {}
		errors = 0
		for field in self.field_list:
			try:
				type_descriptor = field.type_descriptor.check(supercontext)
				assert type_descriptor is not None, "un check() a retourné None"
				self.context[field.name] = type_descriptor
			except semantic.UnresolvableTypeAlias as e:
				errors += 1
				# TODO il faudrait le logger au lieu de le printer à l'arrache
				self.context[field.name] = ErroneousType(field.name)
				print (e)
		if errors > 0:
			print ("il y a eu des erreurs de résolution de types, la compilation ne pourra pas être terminée")

	def lda_format(self, indent=0):
		result = ", ".join(param.lda_format() for param in self.field_list)
		return "<{}>".format(result)

class Identifier:
	def __init__(self, pos, name):
		self.pos = pos
		self.name = name

	def __repr__(self):
		return self.name

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
			return context[self.name]
		except KeyError:
			raise semantic.UnresolvableTypeAlias(self)

class Field(Identifier):
	def __init__(self, ident, type_descriptor):
		super().__init__(ident.pos, ident.name)
		self.type_descriptor = type_descriptor

	def check(self, context):
		raise Exception("on ne peut pas faire d'analyse sémantique sur un field")

	def lda_format(self, indent=0):
		return "{} : {}".format(self.name, self.type_descriptor.lda_format())

class Lexicon:
	def __init__(self, variables=None, composites=None, functions=None):
		self.variables  = variables  if variables  is not None else {}
		self.composites = composites if composites is not None else {}
		self.functions  = functions  if functions  is not None else {}
	
	def check(self, supercontext=None):
		if supercontext is None:
			supercontext = {}
		# TODO : vérif qu'il n'y ait pas 2x le même nom de champ
		# TODO : optionnellement, avertir si on écrase un nom du scope au-dessus
		# fill subcontext with the composites' yet-incomplete contexts
		# so that composites can cross-reference themselves during the next pass
		subcontext = supercontext.copy()
		subcontext.update({name: composite
				for name, composite in self.composites.items()})
		# refine composite subcontexts
		for name, composite in self.composites.items():
			composite.check(subcontext)
		# do the semantic analysis on the variables last so that they can take
		# advantage of the composites that were defined in this lexicon.
		# Put their resolved types in a separate context so that they can't "borrow"
		# another variable's type by using its name as a TypeAlias.
		# TODO - if there are any global variables this will need to be refined.
		# TODO - they might still be able to borrow function return types from the name of the function...
		variable_context = {name: variable.check(subcontext)
				for name, variable in self.variables.items()}
		# merge
		subcontext.update(variable_context)
		return subcontext

	def lda_format(self, indent=0):
		composites = "\n".join("\t{} = {}".format(name, composite.lda_format())
				for name, composite in sorted(self.composites.items()))
		variables = "\n".join("\t{} : {}".format(name, variable.lda_format())
				for name, variable in sorted(self.variables.items()))
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

