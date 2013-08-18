from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestFriendlySyntaxErrors(LDATestCase):
	def test_stray_token_in_while_condition(self):
		program = 'algorithme lexique début tantque ! faire ftant fin'
		expected_pos = program.find('!')
		try:
			mod = self.analyze('module', program)
		except syntax.SyntaxError as error:
			self.assertEquals(error.pos.char, expected_pos)

