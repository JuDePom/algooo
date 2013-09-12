from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Module, Algorithm, Function
from lda.types import Array

class TestArraySemantics(LDATestCase):
	def test_0d(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Array,
				program='tableau entier(**)[]')
	
	def test_1d_constant_intrange(self):
		self.check(cls=Array, program='tableau entier[0..5]')
	
	def test_2d_constant_intrange(self):
		self.check(cls=Array, program='tableau entier[0..5, 0..5]')

	def test_1d_variable_intrange(self):
		# see test_illegal_nested_array_syntax for why this is parsed as an
		# algorithm and not just a lexicon
		self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
				program='algorithme lexique i:entier j:entier t:tableau entier[(**)i..(**)j] début fin')

	def test_wacky_recursive_variable_intrange(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
				program='''algorithme
				lexique t: tableau entier[0..(**)t]
				début fin''')

	def test_1d_variable_intrange_array_as_formal_parameter(self):
		# This has to be checked as a Module and not just as a Function,
		# because we want to catch the error in the function's formal parameters.
		# If we only checked the Function, the error would appear in its lexicon.
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module,
				program='''fonction f(a: tableau entier[0..(**)n], n: entier)
				lexique a: tableau entier[0..n] n: entier début fin''')

	def test_composite_containing_array_type_using_function_level_variable_in_its_dimensions(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
				program='''algorithme
				lexique Moule=<t:tableau entier[0..(**)n]> n:entier
				début fin''')

	def test_non_intrange(self):
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program='tableau entier[(**)1]')
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program='tableau entier[(**)"coucou"]')
		self.assertLDAError(semantic.TypeError, self.check, cls=Array,
				program="tableau entier[(**)'c']")
	
