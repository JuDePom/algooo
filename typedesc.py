class TypeDescriptor:
	pass

class Scalar(TypeDescriptor):
	pass

class Integer(Scalar):
	pass

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
	# Field fields[]
	pass

class TypeAlias(TypeDescriptor):
	pass

class Field:
	def __init__(self, ident, type_descriptor):
		self.name = ident.name
		self.ident = ident
		self.type_descriptor = type_descriptor

class Identifier:
	def __init__(self, pos, name):
		self.pos = pos
		self.name = name
	def __repr__(self):
		return "i_"+self.name

