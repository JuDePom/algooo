from tests.ldatestcase import LDATestCase
from lda.errors import syntax

class TestModuleSyntax(LDATestCase):
	def test_composite_in_module_scope_without_lexicon_keyword(self):
		self.assertLDAError(syntax.SyntaxError, self.check,
				program='(**)Moule = <>')

