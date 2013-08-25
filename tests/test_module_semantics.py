from tests.ldatestcase import LDATestCase
from lda.module import Module
from lda.errors import semantic

class TestModuleSemantics(LDATestCase):
	def test_several_algorithms(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module,
				program='algorithme début fin (**)algorithme début fin')

