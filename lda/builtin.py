"""
Built-in LDA functions.

This module provides the CONTEXT dictionary, which maps LDA built-in function
names to MagicalFunction instances.

The built-in functions are 'magical' in that none of them contain any
statements, and some of them cannot be implemented in pure LDA.
"""

from . import types
from .errors import semantic

class MagicalFunction:
	"""
	Function ersatz that walks like a duck and quacks like a duck.
	
	All magical functions are treated as any other function during the semantic
	analysis phase. Nevertheless, a MagicalFunction differs from a plain
	function in two key areas:

	- Does not contain any LDA statements. The implementation of the function
	is left to the runtime libraries. This allows it to be optimized
	performance-wise and to use system facilities.

	- May possess 'magical' properties that cannot be implemented in pure
	LDA such as being variadic.
	"""

	def __init__(self, return_type, check_func, js_name):
		"""
		:param return_type: function return type
		:param js_name: direct JavaScript translation used in the stock js_call
				method. If the JS equivalent of the magical function is more
				complex than a simple JS function call, you need to override
				the js_call method.
		:param check_func: check_effective_parameters function called by the
				function call operator during semantic analysis
		"""
		self.resolved_type = self
		self.resolved_return_type = return_type
		self.check_effective_parameters = check_func
		self.js_name = js_name

	def js_call(self, pp, call_op):
		"""
		Translate a function call to JavaScript.

		This method simply maps the LDA function call to one JavaScript
		function call (whose name was passed to MagicalFunction.__init__). If
		the JS translation is more complex, override this method.

		:param pp: JSPrettyPrinter object
		:param call_op: FunctionCallOp object (call_op.rhs is the list of
				effective parameters)
		"""
		pp.put(self.js_name, "(")
		pp.join(call_op.rhs, pp.put, ", ")
		pp.put(")")

def pass_through(context, logger, pos, args):
	"""
	Allow all parameters except VOID and BlackHole types.
	"""
	for arg in args:
		if isinstance(arg.resolved_type, types.BlackHole) or \
				arg.resolved_type is types.VOID:
			logger.log(semantic.TypeError(arg.pos,
					"cet argument ne peut pas être passé comme paramètre",
					arg.resolved_type))

PRINT = MagicalFunction(types.VOID, pass_through, "console.log")

SYMBOLS = {
		"écrire": PRINT,
		"ecrire": PRINT,
}

