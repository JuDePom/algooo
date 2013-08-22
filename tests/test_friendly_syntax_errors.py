from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.statements import While

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.check, cls=While,
				program='tantque (**)! faire ftant fin')

