from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestArrayTypeSemantics(LDATestCase):
	def test_0d(self):
		self.assertRaises(semantic.SemanticError, self.check, 'array_type',
			'tableau entier[]')
	
	def test_1d_constant_intrange(self):
		self.check('array_type', 'tableau entier[0..5]')
	
	def test_1d_variable_intrange(self):
		self.check('lexicon', 'lexique i:entier j:entier t:tableau entier[i..j]')
	
	def test_2d_constant_intrange(self):
		self.check('array_type', 'tableau entier[0..5, 0..5]')
	
	def test_non_intrange(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'array_type',
			'tableau entier["coucou"]')
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'array_type',
			"tableau entier['c']")
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'array_type',
			'tableau entier[1]')

