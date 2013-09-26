from lda import types
from lda import semantictools
from lda.errors import semantic

resolved_return_type = types.VOID

def check_effective_parameters(context, logger, pos, args):
	# at least two arguments
	argcount = len(args)
	if argcount < 2:
		logger.log(semantic.ParameterCountMismatch(pos, 2, argcount, at_least=True))
		return
	# first argument must be array
	array_type = args[0].resolved_type
	if not isinstance(array_type, types.Array):
		logger.log(semantic.TypeError(args[0].pos,
				"le premier paramètre de tailletab doit être un tableau dynamique",
				array_type))
		return
	# array must be static
	if array_type.static:
		logger.log(semantic.TypeError(args[0].pos,
				"tailletab ne peut être utilisé qu'avec un tableau "
				"dynamique (et non pas statique)",
				array_type))
		return
	# given dimension count must match array's dimension count
	given_dimcount = argcount - 1
	expected_dimcount = len(array_type.dimensions)
	if given_dimcount != expected_dimcount:
		logger.log(semantic.DimensionCountMismatch(args[0].pos,
				expected_dimcount, given_dimcount))
	# all dimensions must be ranges
	for arg in args[1:]:
		semantictools.enforce("une dimension de tableau dynamique",
				types.RANGE, arg, logger)

def js_call(pp, params):
	pp.put(params[0], " = ")
	params[0].resolved_type.js_new(pp, ((dim.lhs, dim.rhs) for dim in params[1:]))

