from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestArrayTypeSyntax(LDATestCase):
	def test_illegal_nested_array_syntax(self):
		# This one has to be parsed as an entire algorithm, not just as a bare
		# lexicon. This is because a lexicon is delimited by the first unknown
		# token encountered by the parser. By parsing an entire algorithm, the
		# unknown token will be passed back to the algorithm, which won't know
		# what to do with it, and will raise a syntax error.
		self.assert_syntax_error(syntax.SyntaxError, analyze='algorithm',
			program='''algorithme lexique a: tableau(**)tableau entier
				[0..5][0..5] début fin''')

