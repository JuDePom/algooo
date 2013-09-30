from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestFunctionSyntax(LDATestCase):
	def test_missing_return_type(self):
		self.assertLDAError(syntax.ExpectedItem, self.check,
				program="fonction f():(**)début fin")

