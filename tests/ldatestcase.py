import unittest
from lda import parser
from lda import errors

class LDATestCase(unittest.TestCase):
	"""
	LDA program testing facility
	"""

	def setUp(self):
		self.parser = parser.Parser()

	def analyze(self, analyze, program, **kwargs):
		"""
		Parse a program and raise the most relevant syntax error if needed.
		If the program couldn't be parsed in its entirety, an exception
		will be raised.

		:param analyze: The string "analyze_" will be prepended to this in order to
			obtain the full name of the desired analysis method of the Parser class.
			For example, if you want to use "analyze_expression", set this argument
			to "expression".
		:param program: String containing the program itself.
		:param kwargs: Optional arguments to pass to the analysis function.
		"""
		self.parser.set_buf(program)
		analyze_func = getattr(self.parser, 'analyze_' + analyze)
		try:
			with parser.RelevantFailureLogger(self.parser):
				thing = analyze_func(**kwargs)
		except errors.syntax.SyntaxError:
			# TODO get rid of this kludge ASAP (e.g. by decorating all
			# parser methods so that they raise relevant_syntax_error)
			raise self.parser.relevant_syntax_error
		if not self.parser.eof():
			raise Exception("program couldn't be parsed entirely")
		return thing

	def assert_syntax_error(self, error_class, error_marker="(**)", **kwargs):
		"""
		Ensure a syntax error is raised at a specific point in the input program.

		:param error_class  : An instance of this class is expected to be raised
			as an exception during the syntax analysis of the program.
		:param analysis_name: Analysis name passed to LDATestCase.analyze.
		:param program      : String containing the program itself.
		:param error_marker : Substring marking the spot where the syntax error
			is supposed to be raised.
		:param
		"""
		with self.assertRaises(error_class) as cm:
			self.analyze(**kwargs)
		error = cm.exception
		marker_pos = kwargs['program'].find(error_marker)
		self.assertGreaterEqual(marker_pos, 0, "can't find error_marker")
		self.assertEqual(error.pos.char, marker_pos + len(error_marker),
				"exception wasn't raised at expected position")

	def check(self, analysis_name, program, context=None):
		"""
		Perform syntactic and semantic analysis of a program.

		:param analysis_name: Analysis name passed to LDATestCase.analyze.
		:param program: String containing the program itself.
		:param context: Symbol table used by the semantic analysis. If ommitted,
			an empty table will be used.
		"""
		if context is None:
			context = {}
		return self.analyze(analysis_name, program).check(context)

