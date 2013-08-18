from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestCompositeTypeSemantics(LDATestCase):
	def test_duplicate_fields(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'composite_type',
			'Moule = <a:entier, a:chaîne>')

