from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.operators import IntegerRange
from lda.lexicon import Lexicon
from lda.context import ContextStack

class TestIntegerRangeSemantics(LDATestCase):
	def test_fully_constant(self):
		self.check(cls=IntegerRange, program='0..5')

	def test_semi_constant(self):
		context = ContextStack()
		lexicon = self.check(cls=Lexicon, context=context,
				program='lexique n:entier')
		self.check(context, cls=IntegerRange, program='0..n')

	def test_fully_variable(self):
		context = ContextStack()
		lexicon = self.check(cls=Lexicon, context=context,
				program='lexique i:entier j:entier')
		self.check(context, cls=IntegerRange, program='i..j')

	def test_illegal_constant_string_range(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check,
				cls=IntegerRange, program='(**)"coucou".."salut"')

	def test_illegal_constant_real_range(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check,
				cls=IntegerRange, program='(**)1.234..5.678')

	def test_illegal_constant_character_range(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check,
				cls=IntegerRange, program="(**)'a'..'b'")

	def test_illegal_constant_boolean_range(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check,
				cls=IntegerRange, program='(**)vrai..faux')

