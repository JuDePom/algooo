"""
Utility functions to aid semantic analysis
"""

from .errors import semantic


def hunt_duplicates(symbol_list, logger, clash_type):
	"""
	Return a string-symbol dictionary mapped to symbols with unique names.

	Any name used more than once is mapped to `clash_type` in the dictionary
	(typically, types.ERRONEOUS).

	Additionally, log `DuplicateDeclaration` for any symbol using a name
	already used by another symbol in the list.
	"""
	symbol_dict = {}
	dupe_dict = {}
	for item in symbol_list:
		name = item.ident.name
		try:
			dupe_dict[name].append(item)
		except KeyError:
			dupe_dict[name] = [item]
			symbol_dict[item.ident.name] = item
	for dupelist in dupe_dict.values():
		if len(dupelist) > 1:
			pioneer = dupelist[0]
			symbol_dict[pioneer.ident.name] = clash_type
			for dupe in dupelist[1:]:
				logger.log(semantic.DuplicateDeclaration(dupe.ident, pioneer.ident))
	return symbol_dict


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

