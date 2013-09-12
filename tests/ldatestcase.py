import unittest
import subprocess
from io import StringIO
from lda.errors import syntax, semantic, handler
from lda import parser
from lda import types
from lda import symbols
from lda import statements
from lda import expression
from lda import module
from lda import prettyprinter
from lda.context import ContextStack

ERROR_MARKER = "(**)"

PARSING_FUNCTIONS = {
		module.Module:               'analyze_module',
		module.Function:             'analyze_function',
		module.Algorithm:            'analyze_algorithm',
		list:                        'analyze_arglist',
		types.Array:                 'analyze_array',
		types.Composite:             'analyze_composite',
		symbols.Lexicon:             'analyze_lexicon',
		statements.StatementBlock:   'analyze_statement_block',
		statements.While:            'analyze_while',
		statements.For:              'analyze_for',
		statements.If:               'analyze_if',
}

class DefaultOptions:
	case_insensitive = False

class LDATestCase(unittest.TestCase):
	"""
	LDA program testing facility
	"""

	def setUp(self):
		options = DefaultOptions()
		self.parser = parser.Parser(options)

	def analyze(self, program, cls=module.Module, **kwargs):
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
			analyze_func = getattr(self.parser, PARSING_FUNCTIONS[cls])
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

	def assertLDAError(self, error_class, analyzer, **kwargs):
		"""
		Ensure a syntax error is raised at a specific point in the input program.

		In the input program, use the empty comment to mark the spot right
		before the mistake. For example:
			tableau entier[(**)'a']

		:param error_class  : An instance of this class is expected to be raised
			as an exception during the syntax analysis of the program.
		:param kwargs       : Arguments to pass to the analysis function.
		"""
		result = None
		with self.assertRaises(error_class) as cm:
			result = analyzer(**kwargs)
		error = cm.exception
		marker_pos = kwargs['program'].find(ERROR_MARKER)
		self.assertGreaterEqual(marker_pos, 0, "can't find error marker")
		self.assertEqual(error.pos.char, marker_pos + len(ERROR_MARKER),
				"exception wasn't raised at expected position (raised: {})"
				.format(error))
		return result

	def check(self, context=None, **kwargs):
		"""
		Perform syntactic and semantic analysis of a program.

		:param context: Context used by the semantic analysis. If ommitted,
			the default context will be used.
		:param kwargs : Arguments to pass to the analysis function.
		"""
		if context is None:
			context = ContextStack()
		root = self.analyze(**kwargs)
		root.check(context, handler.Raiser())
		return root

	def jseval(self, **kwargs):
		pp = prettyprinter.JSPrettyPrinter()
		self.check(**kwargs).js(pp)
		code = str(pp) + "\n\nMain();\n"
		return subprocess.check_output(["node", "-e", code], universal_newlines=True)

