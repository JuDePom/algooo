from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Algorithm

class TestExpressionSemantics(LDATestCase):
	def test_assignment_must_be_root_node_in_expression(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
				program='''\
						algorithme
						lexique
							a: entier
						début
							si a (**)<- 3 alors
							fsi
						fin
						''')

