import unittest
import lda.parser

class ParserTestCase(unittest.TestCase):
	def setUp(self):
		self.parser = lda.parser.Parser()
	
	def analyze(self, analysis_name, buf):
		self.parser.set_buf(buf)
		analyze = getattr(self.parser, 'analyze_' + analysis_name)
		thing = analyze()
		if not self.parser.eof():
			raise Exception("analyse complète mais il reste des choses derrière")
		return thing

