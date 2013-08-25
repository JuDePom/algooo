from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.module import Module
from lda.statements import While

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=While,
				program='tantque (**)! faire ftant fin')
	
	def test_forgot_lexicon_keyword(self):
		# TODO vérifier qu'il demande "lexique" ! Là il demande "début"
		self.assertLDAError(syntax.ExpectedKeyword, self.analyze, cls=Module,
				program='''\
				algorithme
					(**)n: entier
				début
					n <- 2
				fin''')

	def test_stray_integer_in_module(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, program="(**)3")

