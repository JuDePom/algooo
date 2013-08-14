import unittest
import ldaparser

class ParserTestCase(unittest.TestCase):
	def setUp(self):
		self.parser = ldaparser.Parser()
	
	def analyze(self, analysis_name, buf):
		self.parser.set_buf(buf)
		analyze = getattr(self.parser, 'analyze_' + analysis_name)
		thing = analyze()
		if not self.parser.eof():
			raise Exception("analyse complète mais il reste des choses derrière")
		return thing

