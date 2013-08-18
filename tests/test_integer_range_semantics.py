from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestIntegerRangeSemantics(LDATestCase):
	def test_fully_constant(self):
		self.check('expression', '0..5')
	
	def test_semi_constant(self):
		context = self.check('lexicon', 'lexique n:entier')
		self.check('expression', '0..n', context)
	
	def test_fully_variable(self):
		context = self.check('lexicon', 'lexique i:entier j:entier')
		self.check('expression', 'i..j', context)
	
	def test_illegal_constant_string_range(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'expression',
			'"coucou".."salut"')
	
	def test_illegal_constant_real_range(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'expression',
			'1.234..5.678')
	
	def test_illegal_constant_character_range(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'expression',
			"'a'..'b'")

	def test_illegal_constant_boolean_range(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'expression',
			'vrai..faux')
