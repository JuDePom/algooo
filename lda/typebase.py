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

class ErroneousTypeClass(TypeDescriptor):
	relevant = False

	def __eq__(self, other):
		return False

# TODO: ugly
ErroneousType = ErroneousTypeClass()
AssignmentType = ErroneousTypeClass()

