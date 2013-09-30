from lda import types
from lda.errors import semantic

resolved_return_type = types.VOID

def check_effective_parameters(context, logger, pos, args):
	"""
	Allow all parameters except VOID and BlackHole types.
	"""
	for arg in args:
		if not types.nonvoid(arg.resolved_type):
			logger.log(semantic.TypeError(arg.pos,
					"cet argument ne peut pas être passé comme paramètre",
					arg.resolved_type))

def js_call(pp, params):
	pp.put("console.log(")
	pp.join(params, pp.put, ", ")
	pp.put(")")

