import unittest
from lda import parser, module, expression, types, symbols, statements
from lda.errors import syntax, semantic, handler

class DefaultOptions:
	case_insensitive = False

class LDATestCase(unittest.TestCase):
	"""
	LDA program testing facility
	"""

	def setUp(self):
		options = DefaultOptions()
		self.parser = parser.Parser(options)

		self.parsing_functions = {
				module.Module:               self.parser.analyze_module,
				module.Function:             self.parser.analyze_function,
				module.Algorithm:            self.parser.analyze_algorithm,
				expression.Varargs:          self.parser.analyze_varargs,
				types.Array:                 self.parser.analyze_array,
				types.Composite:             self.parser.analyze_composite,
				symbols.Lexicon:             self.parser.analyze_lexicon,
				statements.While:            self.parser.analyze_while,
				statements.For:              self.parser.analyze_for,
				statements.If:               self.parser.analyze_if,
		}

	def analyze(self, cls, program, **kwargs):
		"""
		Parse a program. Raise the most relevant syntax error if needed.
		If the program was syntactically correct, ensure that:
		- the resulting node is an instance of the class passed as a parameter
		- the program was parsed in its entirety

		:param analyze: The string "analyze_" will be prepended to this in order to
			obtain the full name of the desired analysis method of the Parser class.
			For example, if you want to use "analyze_expression", set this argument
			to "expression".
		:param cls: The expected class of the resulting node.
		:param program: String containing the program itself.
		:param kwargs: Optional arguments to pass to the analysis function.
		"""
		self.parser.set_buf(program)
		try:
			analyze_func = self.parsing_functions[cls]
		except KeyError as e:
			if issubclass(cls, expression.Expression):
				analyze_func = self.parser.analyze_expression
			else:
				raise e
		try:
			with parser.RelevantFailureLogger(self.parser):
				thing = analyze_func(**kwargs)
		except syntax.SyntaxError:
			# TODO get rid of this kludge ASAP (e.g. by decorating all
			# parser methods so that they raise relevant_syntax_error)
			raise self.parser.relevant_syntax_error
		self.assertIsInstance(thing, cls)
		self.assertTrue(self.parser.eof(), ("program couldn't be parsed entirely, "
				"stopped at {}").format(self.parser.pos))
		return thing

	def assertLDAError(self, error_class, analyzer, error_marker="(**)", **kwargs):
		"""
		Ensure a syntax error is raised at a specific point in the input program.

		:param error_class  : An instance of this class is expected to be raised
			as an exception during the syntax analysis of the program.
		:param error_marker : Substring marking the spot where the syntax error
			is supposed to be raised.
		:param kwargs       : Arguments to pass to the analysis function.
		"""
		result = None
		with self.assertRaises(error_class) as cm:
			result = analyzer(**kwargs)
		error = cm.exception
		marker_pos = kwargs['program'].find(error_marker)
		self.assertGreaterEqual(marker_pos, 0, "can't find error_marker")
		self.assertEqual(error.pos.char, marker_pos + len(error_marker),
				"exception wasn't raised at expected position (raised at {})"
				.format(error.pos))
		return result

	def check(self, context=None, **kwargs):
		"""
		Perform syntactic and semantic analysis of a program.

		:param context: Symbol table used by the semantic analysis. If ommitted,
			an empty table will be used.
		:param kwargs : Arguments to pass to the analysis function.
		"""
		if context is None:
			context = {}
		return self.analyze(**kwargs).check(context, handler.Raiser())

