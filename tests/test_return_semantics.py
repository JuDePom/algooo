from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestReturnSemantics(LDATestCase):
	def test_return_nothing_in_algorithm(self):
		self.check(program="""\
				algorithme
				début
					retourne
				fin""")

	def test_return_expression_in_algorithm(self):
		self.assertLDAError(semantic.SemanticError, self.check, program="""\
				algorithme
				début
					retourne (**)3
				fin""")

	def test_return_wrong_type(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, program="""\
				fonction f(): entier
				début
					retourne (**)3.141593
				fin""")

	def test_return_integer_literal_in_function_returning_integer(self):
		self.check(program="fonction f(): entier début retourne 3 fin")

	def test_return_integer_variable_in_function_returning_integer(self):
		self.check(program="""\
				fonction f(): entier
				lexique
					a : entier
				début
					a<-3
					retourne a
				fin""")

	def test_return_nothing_in_function_returning_nothing(self):
		self.check(program="""\
				fonction f()
				début
					retourne
				fin""")

	def test_return_nothing_in_function_returning_integer(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				fonction f(): entier
				début
					(**)retourne
				fin""")

