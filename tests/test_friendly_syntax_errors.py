from tests.ldatestcase import LDATestCase
from lda import kw

class TestFriendlySyntaxErrors(LDATestCase):
	def test_forgot_lexicon_keyword(self):
		# The error itself concerns BEGIN, but in this specific case a tip
		# suggests to try adding LEXICON
		error = self.assertMissingKeywords(kw.BEGIN, program="""\
				algorithme
					(**)n: entier
				début
					n <- 2
				fin""")
		self.assertTrue(hasattr(error, 'tip'))


