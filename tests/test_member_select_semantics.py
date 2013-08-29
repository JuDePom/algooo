from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Module

class TestMemberSelectSemantics(LDATestCase):
	def test_simple_member_select(self):
		self.check(cls=Module, program='''\
				algorithme
				lexique
					Moule = <a: entier>
					m: Moule
				début
					m.a <- 3
				fin''')

