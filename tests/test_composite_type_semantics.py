from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.types import Composite

class TestCompositeTypeSemantics(LDATestCase):
	def test_duplicate_fields_in_composite(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, ident=None, cls=Composite,
				program='<a:entier, (**)a:chaîne>')


