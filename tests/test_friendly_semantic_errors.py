from .ldatestcase import LDATestCase
from lda.errors import semantic

class TestFriendlySemanticErrors(LDATestCase):
	def test_only_1_error_about_erroneous_array_referenced_later(self):
		self.assertMultipleSemanticErrors([semantic.TypeError], """\
				algorithme
				lexique
					t: tableau entier[(**)"xxx"]
					u: tableau entier[0..3]
				début
					t <- u
				fin""")

	def test_3_errors_about_array_with_3_erroneous_dimensions(self):
		self.assertMultipleSemanticErrors(
				[semantic.TypeError, semantic.TypeError, semantic.TypeError],
				"""algorithme
				lexique
					t: tableau entier[(**)"xxx", (**)'a', (**)5.123]
				début fin""")

	def test_1_error_about_undeclared_for_counter_variable(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration],
				"""algorithme
				début
					pour (**)i de 1 jusque 5 faire
					fpour
				fin""")

	def test_1_error_about_undeclared_while_condition_variable(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration],
				"algorithme début tantque (**)i faire ftant fin")

	def test_1_error_for_each_conditional_branch_using_undeclared_variable(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration, semantic.MissingDeclaration],
				"""algorithme
				début
					si (**)i alors
					snsi (**)j alors
					fsi
				fin""")

	def test_1_error_about_assignment_to_undeclared_variable(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration],
				"algorithme début (**)i <- 3 fin")

	def test_1_error_about_arithmetic_on_undeclared_variable(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration],
				"""algorithme lexique j:entier début
					j <- -(**)i
					j <- i + i
				fin""")

	def test_1_error_about_undeclared_variable_used_multiple_times(self):
		self.assertMultipleSemanticErrors(
				[semantic.MissingDeclaration],
				"""algorithme
				lexique
					j: entier
				début
					(**)i <- 1
					tantque i faire ftant
					si i alors fsi
					pour i de 1 à 100 faire fpour
					i <- i + 1
					j <- i + 3
				fin""")

