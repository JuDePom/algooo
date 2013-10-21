from lda import types
from lda.errors import semantic

resolved_return_type = types.VOID

def check_call(context, logger, pos, params):
	"""
	Allow all parameters except VOID and BlackHole types.
	"""
	for p in params:
		p.check(context, logger)
		if not types.nonvoid(p.resolved_type):
			logger.log(semantic.TypeError(p.pos,
					"cet argument ne peut pas être passé comme paramètre",
					p.resolved_type))

def js_call(pp, params):
	pp.put("LDA.print(")
	prefix = "("
	for param in params:
		pp.put(prefix, param, ")")
		prefix = " + \" \" + ("
	pp.put(")")

