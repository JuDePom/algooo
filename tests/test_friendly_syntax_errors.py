from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.module import Module
from lda.statements import While
from lda import kw

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=While,
				program='tantque (**)! faire ftant fin')
	
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

	def test_stray_integer_in_module(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, program="(**)3")

	def test_eof_after_algorithm_lexicon(self):
		self.assertMissingKeywords(kw.BEGIN, program="algorithme lexique(**)")

	def test_eof_in_algorithm_after_begin(self):
		self.assertMissingKeywords(kw.END, program="algorithme début(**)")

