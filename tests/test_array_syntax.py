from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.types import Array

class TestArraySyntax(LDATestCase):
	def test_incomplete_intrange(self):
		self.assertLDAError(syntax.MissingRightOperand, self.analyze, cls=Array,
				program='tableau entier[1 (**)..]')

