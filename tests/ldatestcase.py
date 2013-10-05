import unittest
from lda.errors import syntax, semantic, handler
from lda import parser
from lda import types
from lda import lexicon
from lda import statements
from lda import expression
from lda import module
from lda import function
from lda import prettyprinter
from lda.context import ContextStack
from tests import jsshell

ERROR_MARKER = "(**)"

PARSING_FUNCTIONS = {
		module.Module:               'analyze_module',
		function.Function:           'analyze_function',
		function.Algorithm:          'analyze_algorithm',
		list:                        'analyze_arglist',
		types.Array:                 'analyze_array',
		types.Composite:             'analyze_composite',
		lexicon.Lexicon:             'analyze_lexicon',
		statements.StatementBlock:   'analyze_statement_block',
		statements.While:            'analyze_while',
		statements.For:              'analyze_for',
		statements.If:               'analyze_if',
}

class DefaultOptions:
	ignore_case = False

class LDATestCase(unittest.TestCase):
	"""
	LDA program testing facility
	"""

	def setUp(self):
		self.options = DefaultOptions()

	def analyze(self, program, cls=module.Module, force_eof=True, **kwargs):
		"""
		Parse a program. Raise the most relevant syntax error if needed.
		If the program was syntactically correct, ensure that:
		- the resulting node is an instance of the class passed as a parameter
		- the program was parsed in its entirety

		:param program: String containing the program itself.
		:param cls: The expected class of the resulting node. Implicitly
			determines the analysis method used.
		:param force_eof: If True, the test will fail if the program string was
			only parsed partially.
		:param kwargs: Optional arguments to pass to the analysis function.
		"""
		self.parser = parser.Parser(self.options, raw_buf=program)
		try:
			analyze_func = getattr(self.parser, PARSING_FUNCTIONS[cls])
		except KeyError as e:
			if issubclass(cls, expression.Expression):
				analyze_func = self.parser.analyze_expression
			else:
				raise e
		thing = analyze_func(**kwargs)
		self.assertIsInstance(thing, cls)
		if force_eof:
			self.assertTrue(self.parser.eof(), ("program couldn't be parsed entirely"
					" -- stopped at {}").format(self.parser.pos))
		return thing

	def _assertSingleLDAError(self, program, error, start=0, error_no=0):
		"""
		Meant for LDATestCase's internal use only. Find the next error marker
		and ensure its position matches where the error was effectively found.
		Return the position following the error marker.

		:param start: Where to start looking for the error marker in the
			program (0 by default)
		:param error_no: Error number to help identifying the culprit when
			working with several potential errors (0 by default)
		"""
		marker_pos = program.find(ERROR_MARKER, start)
		expected_pos = marker_pos + len(ERROR_MARKER)
		self.assertNotEqual(-1, marker_pos, "can't find error marker!")
		self.assertEqual(error.pos.char, expected_pos,
				"error #{} wasn't reported at expected position (raised: {})"
				.format(error_no, error))
		return expected_pos

	def assertLDAError(self, error_class, analyzer, **kwargs):
		"""
		Ensure an LDA syntactic or semantic error is raised at a specific point
		in the input program.

		In the input program, use the empty comment to mark the spot right
		before the mistake. For example:
			tableau entier[(**)'a']

		:param error_class  : An instance of this class is expected to be raised
			during the syntactic and semantic analysis of the program.
		:param kwargs       : Arguments to pass to the analysis function.
		"""
		result = None
		with self.assertRaises(error_class) as cm:
			result = analyzer(**kwargs)
		self._assertSingleLDAError(kwargs['program'], cm.exception)
		return cm.exception

	def assertMissingKeywords(self, *expected_keywords, **kwargs):
		"""
		Given a syntactically broken LDA program, ensure the syntax analysis
		fails because a keyword was missing (among a specific set of keywords)
		at a specific point in the input program.

		:param expected_keywords: One of these keywords is expected at the
			error marker comment (see assertLDAError's documentation)
		:param kwargs: Arguments to pass to analyze().
		"""
		error = self.assertLDAError(syntax.ExpectedKeyword, self.analyze, **kwargs)
		self.assertSetEqual(set(error.expected_keywords), set(expected_keywords))
		return error

	def check(self, context=None, error_handler=None, **kwargs):
		"""
		Perform syntactic and semantic analysis of a program.

		:param context: Context used by the semantic analysis. If omitted,
			the default context will be used.
		:param error_handler: Error handler object used during the semantic
			analysis. If omitted, a Raiser object will be used, meaning the first
			encountered error will be raised as an exception.
		:param kwargs : Arguments to pass to the analysis function.
		"""
		if context is None:
			context = ContextStack(self.options)
		if error_handler is None:
			error_handler = handler.Raiser()
		root = self.analyze(**kwargs)
		if hasattr(root, 'resolve_type'):
			root.resolve_type(context, error_handler)
		else:
			root.check(context, error_handler)
		return root

	def jseval(self, shutup=False, extracode="P.main();", **kwargs):
		"""
		Compile a program to JavaScript, execute it, and return the output.
		The input program's entry point is its Algorithm.

		:param shutup: If True, stderr's output will be redirected to
		subprocess.DEVNULL. This is useful if you are certain the test fails.
		:param extracode: Extra JavaScript code executed at the very end of the
		generated code. By default, `extracode` calls `P.main()`.
		"""
		pp = prettyprinter.JSPrettyPrinter()
		self.check(**kwargs).js(pp)
		return jsshell.run(str(pp), shutup=shutup, extracode=extracode)

