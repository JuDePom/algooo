from lda import types
from lda.errors import semantic

# The VOID return type prevents the function call from being placed in the
# middle of an expression. Thus, this call is guaranteed to be the root node of
# an expression. In turn, this allows us to translate this call to a simple JS
# assignment instead of resorting to fake pointer tricks.
resolved_return_type = types.VOID

APICALL = {
	types.INTEGER:   "readInt",
	types.BOOLEAN:   "readBool",
	types.CHARACTER: "readChar",
	types.STRING:    "readStr",
	types.REAL:      "readReal",
}

def check_call(context, logger, pos, params):
	if len(params) != 1:
		logger.log(semantic.ParameterCountMismatch(pos, 1, len(params)))
	var = params[0]
	var.check(context, logger, mode='w')
	if not isinstance(var.resolved_type, types.Scalar):
		logger.log(semantic.TypeError(var.pos, "la fonction magique lire() "
				"ne peut être utilisée qu'avec des types scalaires",
				var.resolved_type))
	if not var.writable:
		logger.log(semantic.NonWritable(var))

def js_call(pp, params):
	assert len(params) == 1 and isinstance(params[0].resolved_type, types.Scalar),\
			"should've called check_call"
	var = params[0]
	pp.put(var, " = LDA.", APICALL[var.resolved_type], "()")

