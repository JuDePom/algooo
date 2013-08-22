from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.typedesc import ArrayType, Lexicon

class TestArrayTypeSemantics(LDATestCase):
	def test_0d(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=ArrayType,
			program='tableau entier[(**)]')
	
	def test_1d_constant_intrange(self):
		self.check(cls=ArrayType, program='tableau entier[0..5]')
	
	def test_1d_variable_intrange(self):
		self.check(cls=Lexicon, program='lexique i:entier j:entier t:tableau entier[i..j]')
	
	def test_2d_constant_intrange(self):
		self.check(cls=ArrayType, program='tableau entier[0..5, 0..5]')
	
	def test_non_intrange(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=ArrayType,
			program='tableau entier[(**)"coucou"]')
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=ArrayType,
			program="tableau entier[(**)'c']")
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=ArrayType,
			program='tableau entier[(**)1]')

