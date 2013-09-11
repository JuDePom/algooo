from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Module

class TestFunctionCallSemantics(LDATestCase):
	def test_wrong_effective_parameter_count_1_instead_of_0(self):
		self.assertLDAError(semantic.ParameterCountMismatch, self.check, cls=Module,
			program='fonction f0() lexique début f0(**)(1) fin')

	def test_wrong_effective_parameter_count_0_instead_of_1(self):
		self.assertLDAError(semantic.ParameterCountMismatch, self.check, cls=Module,
			program='fonction f1(a:entier) lexique a:entier début f1(**)() fin')

	def test_assignment_using_function_call_returning_wrong_type(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, cls=Module,
				program='''fonction f(): entier
				lexique
					Moule = <>
					m: Moule
				début
					m (**)<- f()
				fin''')

	def test_matching_return_type_integer(self):
		self.check(program='''\
				fonction f(): entier
				lexique
					a: entier
				début
					a <- f()
				fin''')

	def test_matching_return_type_composite(self):
		self.check(program='''\
				lexique
					Moule = <>
				fonction f(): Moule
				lexique
					m: Moule
				début
					m <- f()
				fin''')

	def test_mismatching_return_type_composite_1(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, program='''\
				lexique
					Moule = <>
				fonction f(): Moule
				lexique
					a: entier
				début
					a (**)<- f()
				fin''')

	def test_mismatching_return_type_composite_2(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, program='''\
				lexique
					Moule = <>
				fonction f(): entier
				lexique
					a: Moule
				début
					a (**)<- f()
				fin''')

	def test_parameter_type_mismatch_1(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=Module,
				program='''fonction f(a: entier)
				lexique
					Moule = <>
					a: entier
					m: Moule
				début
					f((**)m)
				fin''')

	def test_parameter_type_mismatch_3(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=Module,
				program='''fonction f(a: entier, b: chaîne, c: caractère)
				lexique
					Moule = <>
					a: entier
					b: chaîne
					c: caractère
					m: Moule
				début
					f((**)m, (**)a, (**)m)
				fin''')

	def test_call_non_function_identifier(self):
		self.assertLDAError(semantic.NonCallable, self.check, cls=Module,
				program='''algorithme
				lexique
					a: entier
				début
					a(**)()
				fin''')

	def test_call_non_function_literal(self):
		self.assertLDAError(semantic.NonCallable, self.check, cls=Module,
				program='''algorithme
				début
					3(**)()
				fin''')

	def test_function_call_within_function_call(self):
		self.check(program="""\
				fonction trois(): entier
				début retourne 3 fin

				algorithme
				début
					écrire(trois())
				fin""")

