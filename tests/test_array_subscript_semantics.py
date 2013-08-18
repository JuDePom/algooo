from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestArraySubscriptSemantics(LDATestCase):
	def test_non_subscriptable(self):
		self.assertRaises(semantic.NonSubscriptable, self.check, 'algorithm',
			'algorithme lexique a:entier début a[0] <- 1 fin')

	def test_no_dimensions(self):
		self.assertRaises(semantic.DimensionCountMismatch, self.check, 'algorithm', '''\
			algorithme lexique a: tableau entier[0..5]
			début a[] <- 3 fin''')

	def test_too_few_dimensions(self):
		self.assertRaises(semantic.DimensionCountMismatch, self.check, 'algorithm', '''\
			algorithme lexique a: tableau entier[0..5, 0..5]
			début a[0] <- 3 fin''')
	
	def test_too_many_dimensions(self):
		self.assertRaises(semantic.DimensionCountMismatch, self.check, 'algorithm', '''\
			algorithme lexique a: tableau entier[0..5, 0..5]
			début a[0,0,0] <- 3 fin''')

	def test_non_integer_subscript(self):
		self.assertRaises(semantic.SpecificTypeExpected, self.check, 'algorithm', '''\
			algorithme lexique a: tableau entier[0..5]
			début a[1.234] fin''')

