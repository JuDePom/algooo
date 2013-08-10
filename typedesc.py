import errors

class CanNotBeResolved(Exception):
	pass

class UnresolvableTypeLoop(Exception):
	pass

class TypeDescriptor:
	pass

class Scalar(TypeDescriptor):
	pass

class Integer(Scalar):
	@staticmethod
	def check(context):
		return Integer

class Real(Scalar):
	pass

class Boolean(Scalar):
	pass

class Character(Scalar):
	pass

class String(Scalar):
	pass

class Void(TypeDescriptor):
	pass

class Range(TypeDescriptor):
	# min (expr)
	# max (expr)
	pass

class ArrayType(TypeDescriptor):
	# TypeDescriptor element_type
	# Range dimensions[]
	pass

class CompositeType(TypeDescriptor):
	def __init__(self, field_list):
		self.field_list = field_list
		self.resolved_context = None

	def check(self, context):
		names = [f.name for f in self.field_list]
		dupe_names = [n for n in set(names) if names.count(n) > 1]
		dupe_fields = (f for f in self.field_list if f.name in dupe_names)
		for df in dupe_fields:
			raise errors.LDASemanticError(df.ident.pos, "ce nom de champ "
					"apparaît plusieurs fois dans le type composite")
		unresolved = {f.name: f.type_descriptor for f in self.field_list}
		self.resolved_context = resolve_types(context, unresolved, {})
		return self.resolved_context

def resolve_types(context, unresolved, subcontext=None):
	"""
	TODO write better documentation

	context: symbol table that will be used to try to resolve type aliases.
	Table entries: string --> TypeDescriptor

	unresolved: dictionary (string --> yet unresolved type)
	Will be destroyed.

	subcontext: new symbol table that will be augmented with the resolved types.
	If ommitted, context will receive the resolved types instead.
	"""
	if subcontext is None:
		subcontext = context
	length = len(unresolved)
	while length != 0:
		for k in list(unresolved.keys()):
			try:
				type_descriptor = unresolved[k].check(context)
				if type_descriptor is None:
					raise CanNotBeResolved
				subcontext[k] = type_descriptor
				del unresolved[k]
			except (CanNotBeResolved, UnresolvableTypeLoop):
				pass
		new_length = len(unresolved)
		if new_length == length:
			raise UnresolvableTypeLoop
		length = new_length
	return subcontext

class TypeAlias:
	def __init__(self, ident):
		self.pos = ident.pos
		self.name = ident.name
	def check(self, context):
		try:
			return context[self.name]
		except KeyError:
			raise CanNotBeResolved

class Field:
	# TODO hériter de sourcething ou d'identifier
	def __init__(self, ident, type_descriptor):
		self.name = ident.name
		self.ident = ident
		self.type_descriptor = type_descriptor
	def check(self, context):
		raise Exception("on ne peut pas faire d'analyse sémantique sur un field")

class Identifier:
	def __init__(self, pos, name):
		self.pos = pos
		self.name = name
	def __repr__(self):
		return "i_"+self.name

