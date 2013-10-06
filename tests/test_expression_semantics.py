from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.expression import Expression

class TestExpressionSemantics(LDATestCase):
	def test_type_errors_in_incorrect_expressions(self):
		def test(program):
			self.assertLDAError(semantic.TypeError, self.check,
					cls=Expression, program=program)
		test("non (**)3")
		test("non (**)3.14")
		test("non (**)-3")
		test("non (**)\"toto\"")
		test("non (**)'x'")
		test("(**)-vrai")
		test("(**)-\"bonjour\"")
		test("1 (**)+ 'x'")
		test("1 (**)+ \"x\"")
		test("1 (**)+ vrai")

