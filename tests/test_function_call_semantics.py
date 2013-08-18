from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestFunctionCallSemantics(LDATestCase):
	def test_wrong_effective_parameter_count_1_instead_of_0(self):
		self.assertRaises(semantic.ParameterCountMismatch, self.check, 'module',
			'fonction f0() lexique début f0(1) fin')

	def test_wrong_effective_parameter_count_0_instead_of_1(self):
		self.assertRaises(semantic.ParameterCountMismatch, self.check, 'module',
			'fonction f1(a:entier) lexique début f1() fin')

	def test_wrong_return_type(self):
		self.assertRaises(semantic.TypeMismatch, self.check, 'module', '''\
				fonction f(): entier
				lexique
					Moule = <>
					m: Moule
				début
					m <- f()
				fin''')

	def test_effective_parameter_type_mismatch(self):
		self.assertRaises(semantic.TypeMismatch, self.check, 'module', '''\
				fonction f(a: entier)
				lexique
					Moule = <>
					a: entier
					m: Moule
				début
					f(m)
				fin''')
		self.assertRaises(semantic.TypeMismatch, self.check, 'module', '''\
				fonction f(a: entier, b: chaîne, c: caractère)
				lexique
					Moule = <>
					a: entier
					m: Moule
				début
					f(m, a, m)
				fin''')

	def test_effective_parameter_equivalent_type(self):
		self.check('module', '''\
				fonction f(r: réel)
				lexique
					r: réel
					e: entier
				début
					e <- 50
					f(e)
				fin''')

	def test_calling_non_function(self):
		self.assertRaises(semantic.NonCallable, self.check, 'module', '''\
				algorithme
				lexique
					a: entier
				début
					a()
				fin''')

