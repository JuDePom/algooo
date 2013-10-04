from lda import types
from lda import semantictools
from lda.errors import semantic

resolved_return_type = types.VOID

def check_effective_parameters(logger, pos, params):
	# at least 2 params
	count = len(params)
	if count < 2:
		logger.log(semantic.ParameterCountMismatch(pos, 2, count, at_least=True))
		return
	# first param must be array
	array_type = params[0].resolved_type
	if not isinstance(array_type, types.Array):
		logger.log(semantic.TypeError(params[0].pos,
				"le premier paramètre de tailletab doit être un tableau dynamique",
				array_type))
		return
	# array must be static
	if array_type.static:
		logger.log(semantic.TypeError(params[0].pos,
				"tailletab ne peut être utilisé qu'avec un tableau "
				"dynamique (et non pas statique)",
				array_type))
		return
	# given dimension count must match array's dimension count
	given_dimcount = count - 1
	expected_dimcount = len(array_type.dimensions)
	if given_dimcount != expected_dimcount:
		logger.log(semantic.DimensionCountMismatch(params[0].pos,
				expected_dimcount, given_dimcount))
	# all dimensions must be ranges
	for p in params[1:]:
		semantictools.enforce("une dimension de tableau dynamique",
				types.RANGE, p, logger)

def js_call(pp, params):
	pp.put(params[0], " = ")
	params[0].resolved_type.js_new(pp, ((dim.lhs, dim.rhs) for dim in params[1:]))

