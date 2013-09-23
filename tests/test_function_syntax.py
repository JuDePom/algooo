from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.module import Function

class TestFunctionSyntax(LDATestCase):
	def test_missing_return_type(self):
		self.assertLDAError(syntax.ExpectedItem, self.check, cls=Function,
				program="fonction f():(**)début fin")

