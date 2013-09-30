from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.types import Array

class TestArraySemantics(LDATestCase):
	def test_0d(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Array,
				program='(**)tableau entier[]')
	
	def test_1d_constant_intrange(self):
		self.check(cls=Array, program='tableau entier[0..5]')
	
	def test_2d_constant_intrange(self):
		self.check(cls=Array, program='tableau entier[0..5, 0..5]')

	def test_non_intrange(self):
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program='tableau entier[(**)1]')
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program='tableau entier[(**)"coucou"]')
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program="tableau entier[(**)'c']")
	
	def test_part_dynamic_part_static(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Array,
				program="tableau entier[0..5, (**)?]")
		self.assertLDAError(semantic.SemanticError, self.check, cls=Array,
				program="tableau entier[?, 0(**)..5, ?, 0..3]")

