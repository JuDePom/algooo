from tests.ldatestcase import LDATestCase
from lda.module import Module
from lda.errors import semantic

class TestCaseInsensitivity(LDATestCase):
	def setUp(self):
		super().setUp()
		self.options.case_insensitive = True
	
	def test_case_insensitive_1(self):
		self.check(cls=Module, program="""\
				LEXIQUE
					MOULe = <A: ENTIER>
				ALGORITHME
				LeXiQuE
					M: mOULE
				DÉBuT
					m.a <- 290382432
				FIN""")
	
	def test_case_insensitive_name_clash(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Module,
				program="""lexique
					bonjour: entier
					(**)Bonjour: entier""")

