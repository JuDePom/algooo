from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestFormalParameterSemantics(LDATestCase):
	def test_formal_parameter_absent_from_lexicon(self):
		self.assertRaises(semantic.SemanticError, self.check, 'function',
			'fonction f(a: entier) lexique début fin')

	def test_scalar_formal_parameter_present_in_lexicon(self):
		self.check('function', 'fonction f(a: entier) lexique a: entier début fin')

	def test_fixed_array_formal_parameter_present_in_lexicon(self):
		self.check('function', '''fonction f(a: tableau entier[0..5])
			lexique a: tableau entier[0..5] début fin''')

	def test_array_of_unknown_size_formal_parameter_present_in_lexicon(self):
		self.check('function', '''fonction f(a: tableau entier[0..n], n: entier)
			lexique a: tableau entier[0..n] n: entier début fin''')

	def test_formal_parameter_different_type_in_lexicon(self):
		self.assertRaises(semantic.TypeMismatch, self.check, 'function',
			'fonction f(a: entier) lexique a: réel début fin')

	def test_duplicate_formal_parameter_inside_parentheses(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'function',
			'fonction f(a: entier, a:entier) lexique a: entier début fin')

	def test_formal_parameter_uses_external_type_descriptor(self):
		self.check('module', '''\
				Moule = <>
				fonction f(m: Moule) lexique m: Moule début fin''')

