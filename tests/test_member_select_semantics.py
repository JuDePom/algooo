from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestMemberSelectSemantics(LDATestCase):
	def test_simple_member_select(self):
		self.check(program="""\
				algorithme
				lexique
					Moule = <a: entier>
					m: Moule
				début
					m.a <- 3
				fin""")

	def test_select_non_existant_member(self):
		self.assertLDAError(semantic.MissingDeclaration, self.check, program="""\
				algorithme
				lexique
					Moule = <a: entier>
					m: Moule
				début
					m.(**)b <- 3
				fin""")

