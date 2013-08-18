from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestArrayTypeSyntax(LDATestCase):
	def test_illegal_nested_array_syntax(self):
		self.assertRaises(syntax.SyntaxError, self.analyze, 'lexicon',
			'lexique a: tableau tableau entier[0..5][0..5]')

