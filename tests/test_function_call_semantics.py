from tests.parsertestcase import ParserTestCase
import lda

class test_function_call_semantics(ParserTestCase):
	def test_wrong_effective_parameter_count_1_instead_of_0(self):
		module = self.analyze('module', "fonction f0() lexique début f0(1) fin")
		self.assertRaises(lda.errors.LDASemanticError, module.check)

	def test_wrong_effective_parameter_count_0_instead_of_1(self):
		module = self.analyze('module', "fonction f1(a:entier) lexique début f1() fin")
		self.assertRaises(lda.errors.LDASemanticError, module.check)

	def test_wrong_return_type(self):
		module = self.analyze('module', '''\
				fonction f(): entier
				lexique
					Moule = <>
					m: Moule
				début
					m <- f()
				fin''')
		self.assertRaises(lda.errors.LDASemanticError, module.check)

	def test_effective_parameter_type_mismatch(self):
		module = self.analyze('module', '''\
				fonction f(a: entier)
				lexique
					Moule = <>
					a: entier
					m: Moule
				début
					f(m)
				fin''')
		self.assertRaises(lda.errors.LDASemanticError, module.check)

	def test_effective_parameter_equivalent_type(self):
		module = self.analyze('module', '''\
				fonction f(r: réel)
				lexique
					r: réel
					e: entier
				début
					e <- 50
					f(e)
				fin''')
		module.check()

	def test_calling_non_function(self):
		module = self.analyze('module', '''\
				algorithme
				lexique
					a: entier
				début
					a()
				fin''')
		self.assertRaises(lda.errors.LDASemanticError, module.check)

