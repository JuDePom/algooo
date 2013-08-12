import errors
import position

class CanNotBeResolved(errors.LDASemanticError):
	def __init__(self, alias):
		super().__init__(alias.pos, "nom de type inconnu : \"{}\"".format(alias))
	def add_errors_to(self, what):
		what.append(self)

class TypeDescriptor:
	pass

class ErroneousType(TypeDescriptor):
	def __init__(self, name):
		self.name = name

class Scalar(TypeDescriptor):
	pass

class Integer(Scalar):
	@staticmethod
	def check(context):
		return Integer

	@staticmethod
	def equivalent(other):
		return other == Integer or other == Real

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
	def __init__(self, element_type, dimensions):
		self.element_type = element_type
		self.dimensions = dimensions

	def check(self, context):
		if len(self.dimensions) == 0:
			raise LDASemanticError("un tableau doit avoir au moins une dimension")
		for dim in self.dimensions:
			dim_type = dim.check(context)
		# TODO kludgey
		self.resolved_element_type = self.element_type.check(context)
		return self

class FunctionType(TypeDescriptor):
	def __init__(self, domain, codomain):
		raise NotImplementedError #TODO ASAP

class Context:
	def __init__(self, master=None):
		if master is None:
			self.context = {}
		elif isinstance(master, Context):
			self.context = master.context.copy()
		else:
			self.context = master.copy()
		self.full = False
	
	def __getitem__(self, index):
		return self.context[index]

	def __setitem__(self, index, item):
		self.context[index] = item

	def __delitem__(self, index):
		del self.context[index]

	def __repr__(self):
		return str(self.full) + self.context.__repr__()
	
	def unresolved(self):
		# must be a list and not a generator
		return [k for k, v in self.context.items() if isinstance(v, ErroneousType)]

	def refine(self, supercontext, checkables):
		errors = 0
		for k in self.unresolved():
			try:
				type_descriptor = checkables[k].check(supercontext)
				assert type_descriptor is not None, "un check() a retourné None"
				self[k] = type_descriptor
			except CanNotBeResolved as e:
				errors += 1
				# TODO il faudrait le logger au lieu de le printer à l'arrache
				print (e)
		self.full = errors == 0
	
	def update(self, other):
		self.context.update(other.context)
		if self.full:
			self.full = other.full

class CompositeType(Context, TypeDescriptor):
	def __init__(self, field_list):
		Context.__init__(self, {f.name: ErroneousType(f.name) for f in field_list})
		self.field_list = field_list

	def duplicate_fields(self):
		names = [f.name for f in self.field_list]
		dupe_names = [n for n in set(names) if names.count(n) > 1]
		return (f for f in self.field_list if f.name in dupe_names)

	def check(self, supercontext):
		for df in self.duplicate_fields():
			raise errors.LDASemanticError(df.ident.pos, "ce nom de champ "
					"apparaît plusieurs fois dans le type composite")
		descriptors = {f.name: f.type_descriptor for f in self.field_list}
		self.refine(supercontext, descriptors)
		return self

	def __repr__(self):
		return "CompositeType<{}>".format(self)

class TypeAlias:
	def __init__(self, ident):
		self.pos = ident.pos
		self.name = ident.name
	def check(self, context):
		try:
			return context[self.name]
		except KeyError:
			raise CanNotBeResolved(self)
	def __repr__(self):
		return "TypeAlias<" + self.name + ">"

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
	def check(self, context):
		return context[self.name]

class Lexicon:
	def __init__(self, variables=None, composites=None, functions=None):
		self.variables  = variables  if variables  is not None else {}
		self.composites = composites if composites is not None else {}
		self.functions  = functions  if functions  is not None else {}

		self.context = Context()
		for k in self.variables.keys():
			self.context[k] = ErroneousType(k)
		for k in self.composites.keys():
			self.context[k] = ErroneousType(k)
		for k in self.functions.keys():
			self.context[k] = ErroneousType(k)
	
	def check(self, supercontext=None):
		if supercontext is None:
			supercontext = Context()
		# TODO : vérif qu'il n'y ait pas 2x le même nom de champ
		# TODO : optionnellement, avertir si on écrase un nom du scope au-dessus
		subcontext = Context(supercontext)
		# fill top_context with the composites' yet-incomplete contexts
		# so that composites can cross-reference themselves during the next pass
		for name, composite in self.composites.items():
			subcontext[name] = composite
		# refine composite subcontexts
		for name, composite in self.composites.items():
			composite.check(subcontext)
		# do the semantic analysis on the variables last so that they can take
		# advantage of the composites that were defined in this lexicon.
		# Put their resolved types in a separate context so that they can't "borrow"
		# another variable's type by using its name as a TypeAlias.
		# TODO - if there are any global variables this will need to be refined.
		# TODO - they might still be able to borrow function return types from the name of the function...
		variable_context = Context()
		for name, variable in self.variables.items():
			variable_context[name] = variable.check(subcontext)
		# merge
		subcontext.update(variable_context)
		return subcontext

