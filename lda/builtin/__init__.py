"""
Built-in pseudo-functions.

This module provides the SYMBOLS dictionary, which maps LDA built-in function
names to their implementations.

All built-in functions are implemented as modules, and they are treated as any
other function during the semantic analysis phase because they expose the same
attributes as standard functions. Nevertheless, a built-in function differs
from a plain function in two key areas:

- Does not contain any LDA statements. The actual body of the function is left
to the runtime libraries. This allows it to be optimized performance-wise and
to use system facilities.

- May possess 'magical' properties that cannot be implemented in pure LDA such
as being variadic.

Built-in functions are implemented as modules; each module must expose the
following attributes, in order to mimic an actual function:

- resolved_return_type
- check_effective_parameters(context, logger, pos, args)
- js_call(pp, call_op)

See Function's docstrings for more info about the contract of the functions
mentioned above.
"""

from . import print, arrayalloc

SYMBOLS = {
	"écrire": print,
	"ecrire": print,
	"tailletab": arrayalloc,
}

