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

	def test_wrong_return_type(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, cls=Module,
				program='''fonction f(): entier
				lexique
					Moule = <>
					m: Moule
				début
					m <- f(**)()
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

	def test_calling_non_function(self):
		self.assertLDAError(semantic.NonCallable, self.check, cls=Module,
				program='''algorithme
				lexique
					a: entier
				début
					a(**)()
				fin''')

