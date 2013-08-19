from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		self.assert_syntax_error(syntax.ExpectedItem, analyze='while',
				program='tantque (**)! faire ftant fin')

