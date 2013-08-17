from tests.parsertestcase import ParserTestCase
import lda

class test_lexicon_semantics(ParserTestCase):
	def test_formal_parameter_absent_from_lexicon(self):
		func = self.analyze('function', 'fonction f(a: entier) lexique début fin')
		self.assertRaises(lda.errors.LDASemanticError, func.check, {})

	def test_formal_parameter_present_in_lexicon(self):
		func = self.analyze('function', 'fonction f(a: entier) lexique début fin')
		func.check({})

	def test_variable_absent_from_lexicon(self):
		alg = self.analyze('algorithm', 'algorithme lexique début a <- 3 fin')
		self.assertRaises(lda.errors.LDASemanticError, alg.check, {})

	def test_undefined_type_alias(self):
		mod = self.analyze('module', 'algorithme lexique m: TypeMysterieux début fin')
		self.assertRaises(lda.errors.LDASemanticError, mod.check)

