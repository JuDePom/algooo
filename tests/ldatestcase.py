import unittest
from lda import parser
from lda import errors

class LDATestCase(unittest.TestCase):
	def setUp(self):
		self.parser = parser.Parser()

	def analyze(self, analysis_name, buf, *extra_analysis_args):
		self.parser.set_buf(buf)
		analyze = getattr(self.parser, 'analyze_' + analysis_name)
		try:
			with parser.RelevantFailureLogger(self.parser):
				thing = analyze(*extra_analysis_args)
		except errors.syntax.SyntaxError:
			# TODO get rid of this kludge ASAP (e.g. by decorating all
			# parser methods so that they raise relevant_syntax_error)
			raise self.parser.relevant_syntax_error
		if not self.parser.eof():
			raise Exception("analyse complète mais il reste des choses derrière")
		return thing

	def check(self, analysis_name, buf, context=None):
		if context is None:
			context = {}
		return self.analyze(analysis_name, buf).check(context)

