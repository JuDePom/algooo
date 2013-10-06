from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda import kw

class TestFriendlySyntaxErrors(LDATestCase):
	def test_forgot_lexicon_keyword(self):
		# The error itself concerns BEGIN, but in this specific case a tip
		# suggests to try adding LEXICON
		error = self.assertLDAError(syntax.ExpectedKeyword, analyzer=self.check,
				program="""\
				algorithme
					(**)n: entier
				début
					n <- 2
				fin""")
		self.assertIsInstance(error, syntax.ExpectedKeyword)
		self.assertEqual(set(error.expected_keywords), set([kw.BEGIN]))
		self.assertTrue(hasattr(error, 'tip'))
