from . import kw
from . import types
from . import semantictools
from .errors import semantic
from .operators import GreaterOrEqual, _Addition
from .expression import LiteralInteger

#######################################################################
#
# STATEMENT-RELATED CLASSES
#
#######################################################################

class StatementBlock:
	def __init__(self, pos, body):
		self.pos = pos
		self.body = body

	def __iter__(self):
		for statement in self.body:
			yield statement

	def __bool__(self):
		return bool(self.body)

	def lda(self, pp):
		pp.join(self.body, pp.newline)

	def js(self, pp):
		pp.join(self.body, pp.newline)

	def check(self, context, logger):
		"""
		Check all child statements and set the `returns` attribute if one of
		them returns.
		"""
		self.returns = False
		warned = False
		for statement in self:
			statement.check(context, logger)
			if self.returns and not warned:
				logger.log(semantic.UnreachableStatement(statement.pos))
				warned = True
			self.returns |= statement.returns

class Conditional(StatementBlock):
	"""
	Statement containing a condition and a statement block. The statement
	block is only executed if the condition is verified.
	"""

	def __init__(self, pos, condition, body):
		super().__init__(pos, body)
		self.condition = condition

	def check(self, context, logger):
		self.condition.check(context, logger)
		semantictools.enforce("la condition", types.BOOLEAN, self.condition, logger)
		super().check(context, logger)


#######################################################################
#
# SELF-CONTAINED STATEMENTS
#
#######################################################################

class Assignment:
	returns = False

	def __init__(self, pos, lhs, rhs):
		self.pos = pos
		self.lhs = lhs
		self.rhs = rhs

	def check(self, context, logger):
		self.lhs.check(context, logger, mode='w')
		self.rhs.check(context, logger)
		ltype = self.lhs.resolved_type
		rtype = self.rhs.resolved_type
		if not ltype.compatible(rtype):
			logger.log(semantic.TypeMismatch(self.pos, "le type de l'opérande de "
					"droite doit être compatible avec le type de l'opérande de gauche",
					ltype, rtype))

	def lda(self, pp):
		pp.put(self.lhs, " ", kw.ASSIGN, " ", self.rhs)

	def js(self, pp, semicolon=True):
		try:
			# Try using LHS's JS export method specific to assignments
			self.lhs.js_assign_lhs(pp, self)
		except AttributeError:
			# Fall back to standard JS assignment statement
			pp.put(self.lhs, " = ", self.rhs)
		if semicolon:
			pp.put(";")


class Return:
	"""
	Return statement.

	May own an expression or not, in which case self.expression is None.
	"""

	returns = True

	def __init__(self, pos, expr):
		self.pos = pos
		self.expression = expr

	def lda(self, pp):
		pp.put(kw.RETURN)
		if self.expression is not None:
			pp.put(" ", self.expression)

	def js(self, pp):
		if self.expression is not None:
			pp.put("return ", self.expression, ";")
		else:
			pp.put("return;")

	def check(self, context, logger):
		if self.expression is not None:
			self.expression.check(context, logger)
		# The return statement may only occur in a context owned by an algorithm
		# or a function, so if the assertion below fails, we have a compiler bug.
		assert hasattr(context.parent, "check_return"), "please implement check_return()"
		# Even if the expression is None, we still need to pass it on to the
		# parent in order to decide whether an empty return value is OK.
		context.parent.check_return(logger, self)


class FunctionCallWrapper:
	"""
	Wrapper for a FunctionCall as a standalone statement.

	FunctionCall operators that are not the root of an expression must not use
	this class.
	"""
	returns = False

	def __init__(self, call_op):
		self.pos = call_op.pos
		self.call_op = call_op

	def lda(self, pp):
		pp.put(self.call_op)

	def js(self, pp):
		pp.put(self.call_op, ";")

	def check(self, context, logger):
		self.call_op.check(context, logger)


#######################################################################
#
# META-STATEMENTS (statements that contain other statements)
#
#######################################################################

class If:
	def __init__(self, conditionals, else_block=None):
		self.pos = conditionals[0].pos
		self.conditionals = conditionals
		self.else_block = else_block

	def check(self, context, logger):
		self.returns = True
		for clause in self.conditionals:
			clause.check(context, logger)
			self.returns &= clause.returns
		if self.else_block is not None:
			self.else_block.check(context, logger)
			self.returns &= self.else_block.returns
		else:
			self.returns = False

	def lda(self, pp):
		intro = kw.IF
		for conditional in self.conditionals:
			pp.putline(intro, " ", conditional.condition, " ", kw.THEN)
			pp.indented(pp.putline, conditional)
			intro = kw.ELIF
		if self.else_block:
			pp.putline(kw.ELSE)
			pp.indented(pp.putline, self.else_block)
		pp.put(kw.END_IF)

	def js(self, pp):
		intro = "if ("
		for conditional in self.conditionals:
			pp.putline(intro, conditional.condition, ") {")
			pp.indented(pp.putline, conditional)
			intro = "} else if ("
		if self.else_block:
			pp.putline("} else {")
			pp.indented(pp.putline, self.else_block)
		pp.put("}")

class For(StatementBlock):
	_COMPONENT_NAMES = [
			"le compteur de la boucle",
			"la valeur initiale du compteur",
			"la valeur finale du compteur"
	]

	def __init__(self, pos, counter, initial, final, body):
		super().__init__(pos, body)
		self.counter = counter
		self.initial = initial
		self.final = final

	def check(self, context, logger):
		# Check each component
		self.counter.check(context, logger, mode='w')
		self.initial.check(context, logger)
		self.final.check(context, logger)
		# Ensure they are all integers
		components = [self.counter, self.initial, self.final]
		for comp, name in zip(components, For._COMPONENT_NAMES):
			semantictools.enforce(name, types.INTEGER, comp, logger)
		super().check(context, logger)

	def lda(self, pp):
		pp.putline(kw.FOR, " ", self.counter, " ", kw.FROM, " ", self.initial,
				" ", kw.TO, " ", self.final, " ", kw.DO)
		if self.body:
			pp.indented(pp.putline, super())
		pp.put(kw.END_FOR)

	def js(self, pp):
		"""
		In LDA code, the behavior of a For loop is described with syntactic sugar
		to initialize the counter and to specify the stop condition. The increment
		operation is deduced by the compiler.

		Internally, the behavior of the For loop is distilled into synthetic
		semantic units that could have been written in pure LDA:
		- synth_init: synthetic counter initializing statement (could have been
		  written in LDA as e.g. "i <- 3")
		- synth_cond: synthetic stop condition expression (could have been written
		  in LDA as e.g. "i >= 5")
		- synth_incr: synthetic counter increment statement (could have been
		  written in LDA as e.g. "i <- i + 1")

		The synthetic units facilitate exporting the counter logic to JavaScript,
		because the counter may require specific JS syntax to access it. For
		example, if the counter is an array element, the special syntax to
		initialize it will be handled by the Assignment class.
		"""
		# Create synthetic assignments and condition
		synth_init = Assignment(None, self.counter, self.initial)
		synth_cond = GreaterOrEqual(None, self.counter, self.final)
		synth_cond.root = True
		synth_incr = Assignment(None, self.counter,
				_Addition(None, self.counter, LiteralInteger(None, 1)))
		pp.put("for (")
		synth_init.js(pp, False)
		pp.put("; true; ")
		synth_incr.js(pp, False)
		pp.putline(") {")
		if self.body:
			pp.indented(pp.putline, super())
		# The stop condition is checked before incrementing the counter, so
		# that when the for loop finishes, the counter variable is left at its
		# last useful value.
		pp.indented(pp.putline, "if (", synth_cond, ") break;")
		pp.put("}")

class While(Conditional):
	def lda(self, pp):
		pp.putline(kw.WHILE, " ", self.condition, " ", kw.DO)
		if self.body:
			pp.indented(pp.putline, super())
		pp.put(kw.END_WHILE)

	def js(self, pp):
		pp.putline("while (", self.condition, ") {")
		if self.body:
			pp.indented(pp.putline, super())
		pp.put("}")

