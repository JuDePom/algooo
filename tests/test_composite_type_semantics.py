from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.typedesc import CompositeType
from lda.module import Module

class TestCompositeTypeSemantics(LDATestCase):
	def test_cyclic_composite(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module,
			program='algorithme lexique Moule = <m: (**)Moule> début fin')

	def test_duplicate_fields_in_composite(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=CompositeType,
			program='Moule = <a:entier, (**)a:chaîne>')

