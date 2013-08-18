from tests.ldatestcase import LDATestCase
from lda import module
from lda.errors import syntax

class TestModuleSyntax(LDATestCase):
	def test_several_algorithms(self):
		self.assertRaises(syntax.SyntaxError, self.check, 'module', '''\
				algorithme lexique début fin
				algorithme lexique début fin''')

