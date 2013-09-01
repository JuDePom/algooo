from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.statements import While

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=While,
				program='tantque (**)! faire ftant fin')

	def test_stray_integer_in_module(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, program="(**)3")

