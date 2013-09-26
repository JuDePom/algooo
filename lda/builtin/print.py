from lda import types
from lda.errors import semantic

resolved_return_type = types.VOID

def check_effective_parameters(context, logger, pos, args):
	"""
	Allow all parameters except VOID and BlackHole types.
	"""
	for arg in args:
		if isinstance(arg.resolved_type, types.BlackHole) or \
				arg.resolved_type is types.VOID:
			logger.log(semantic.TypeError(arg.pos,
					"cet argument ne peut pas être passé comme paramètre",
					arg.resolved_type))

def js_call(pp, call_op):
	"""
	Translate a function call to JavaScript.

	This method simply maps the LDA function call to one JavaScript
	function call (whose name was passed to MagicalFunction.__init__). If
	the JS translation is more complex, override this method.

	:param pp: JSPrettyPrinter object
	:param call_op: FunctionCallOp object (call_op.rhs is the list of
			effective parameters)
	"""
	pp.put("console.log(")
	pp.join(call_op.rhs, pp.put, ", ")
	pp.put(")")

