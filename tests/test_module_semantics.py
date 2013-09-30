from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestModuleSemantics(LDATestCase):
	def test_several_algorithms(self):
		self.assertLDAError(semantic.SemanticError, self.check,
				program='algorithme début fin (**)algorithme début fin')

