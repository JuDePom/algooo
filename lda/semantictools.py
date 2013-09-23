"""
Utility functions to aid semantic analysis
"""

from .errors import semantic

def hunt_duplicates(item_list, logger):
	"""
	Log DuplicateDeclaration for any item using a name already used by another
	item in the list.
	"""
	seen = {}
	for item in item_list:
		name = item.ident.name
		try:
			pioneer = seen[name]
			logger.log(semantic.DuplicateDeclaration(item.ident, pioneer.ident))
		except KeyError:
			seen[name] = item

def _enforce(name, expected_type, typed_object, logger, cmpfunc):
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

