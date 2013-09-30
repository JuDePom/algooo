from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestCaseInsensitivity(LDATestCase):
	def setUp(self):
		super().setUp()
		self.options.ignore_case = True
	
	def test_case_insensitive_1(self):
		self.check(program="""\
				(*% ignore_case True %*)
				LEXIQUE
					MOULe = <A: ENTIER>
				ALGORITHME
				LeXiQuE
					M: mOULE
				DÉBuT
					m.a <- 290382432
				FIN""")
	
	def test_case_insensitive_name_clash(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check,
				program="""\
				(*% ignore_case True %*)
				lexique
					bonjour: entier
					(**)Bonjour: entier""")

