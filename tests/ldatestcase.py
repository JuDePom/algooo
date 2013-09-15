import unittest
import subprocess
from io import StringIO
from itertools import count
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

	def assertMultipleSemanticErrors(self, error_classes, program):
		"""
		Ensure that multiple LDA semantic errors are raised at specific points
		in the input program.

		In the unit test's LDA source code, mark expected error occurences with
		an empty comment like so:
			tableau entier[(**)'a', (**)'b']

		Please note that non-relevant errors are ignored by this method. Refer
		to errors/semantic.py to learn how the compiler deems a semantic error
		relevant or not.

		:param error_classes: List of error classes expected to be raised
			during the semantic analysis of the program, in the order in which they
			appear in the program.
		:param program: Source code to analyze.
		"""
		logger = handler.Logger()
		self.check(program=program, error_handler=logger)
		errors = list(logger.relevant_errors)
		# make sure the analysis raised as many errors as expected
		expected_count, reported_count = len(error_classes), len(errors)
		self.assertEqual(expected_count, reported_count,
				"we expected {} errors but only {} were reported".format(
				expected_count, reported_count))
		# check each error
		start = 0
		for i, error, class_ in zip(count(), errors, error_classes):
			start = self._assertSingleLDAError(program, error, start, i)
			self.assertIsInstance(error, class_,
					"wrong error found at error marker #{}".format(i))
		# make sure there are no leftover markers in the source code
		self.assertEqual(-1, program.find(ERROR_MARKER, start),
				"too many error markers!")

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
			context = ContextStack()
		if error_handler is None:
			error_handler = handler.Raiser()
		root = self.analyze(**kwargs)
		if hasattr(root, 'resolve_type'):
			root.resolve_type(context, error_handler)
		else:
			root.check(context, error_handler)
		return root

	def jseval(self, **kwargs):
		pp = prettyprinter.JSPrettyPrinter()
		self.check(**kwargs).js(pp)
		code = str(pp) + "\n\nMain();\n"
		return subprocess.check_output(["node", "-e", code], universal_newlines=True)

