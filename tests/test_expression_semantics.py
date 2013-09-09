from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Algorithm

class TestExpressionSemantics(LDATestCase):
	def test_composite_arithmetic_with_other_composite_of_same_type(self):
		self.assertLDAError(semantic.SemanticError, self.check, program="""\
				algorithme
				lexique
					Moule = <>
					m1: Moule
					m2: Moule
				début
					m1 = m1 (**)+ m2
				fin""")

	def test_composite_arithmetic_with_itself(self):
		self.assertLDAError(semantic.SemanticError, self.check, program="""\
				algorithme
				lexique
					Moule = <>
					m1: Moule
				début
					m1 = m1 (**)+ m1
				fin""")

	def test_reassign_composite_alias_to_other_composite_alias(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				algorithme
				lexique
					Moule = <>
					Huitre = <>
				début
					Moule (**)<- Huitre
				fin""")

	def test_reassign_composite_alias_to_itself(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				algorithme
				lexique
					Moule = <>
				début
					Moule (**)<- Moule
				fin""")

	def test_reassign_function(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				fonction f() début fin
				fonction g() début fin
				algorithme
				début
					f (**)<- g
				fin""")

	def test_assign_to_literal(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				algorithme
				début
					3 (**)<- 4
				fin""")

	def test_assign_to_non_writable_expression(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				algorithme
				début
					3 (**)+ 2 <- 4
				fin""")

