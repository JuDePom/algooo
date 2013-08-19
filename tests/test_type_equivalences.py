from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.typedesc import *

class TestTypeEquivalences(LDATestCase):
	def _test_self_compatibility(self, a):
		self.assertEqual(a, a.equivalent(a))

	def _test_compatibility_both_ways(self, weak, strong):
		self.assertEqual(strong, strong.equivalent(weak))
		self.assertEqual(strong, weak.equivalent(strong))
	
	def _test_conflict_both_ways(self, a, b):
		self.assertIsNone(a.equivalent(b))
		self.assertIsNone(b.equivalent(a))

	def test_integer_compatible_with_itself(self):
		self._test_self_compatibility(Integer)

	def test_integer_weaker_than_real(self):
		self._test_compatibility_both_ways(Integer, Real)

	def test_character_weaker_than_string(self):
		self._test_compatibility_both_ways(Character, String)

	def test_integer_incompatible_with_non_numbers(self):
		self._test_conflict_both_ways(Integer, String)
		self._test_conflict_both_ways(Integer, Character)
		self._test_conflict_both_ways(Integer, Boolean)
		raise NotImplementedError # composite
		raise NotImplementedError # array

	def test_real_incompatible_with_non_numbers(self):
		self._test_conflict_both_ways(Real, String)
		self._test_conflict_both_ways(Real, Character)
		self._test_conflict_both_ways(Real, Boolean)
		raise NotImplementedError # composite
		raise NotImplementedError # array

	def test_string_incompatible_with_composite(self):
		raise NotImplementedError

	def test_composite_compatible_with_itself(self):
		raise NotImplementedError

	def test_array_compatible_with_itself(self):
		array = self.analyze('array_type', 'tableau entier[0..5]')
		self.assertIsInstance(array, ArrayType)
		self._test_self_compatibility(array)

	def test_array_incompatible_with_array_of_same_type_and_different_dimensions(self):
		array1d = self.analyze('array_type', 'tableau entier[0..5]')
		array2d = self.analyze('array_type', 'tableau entier[0..5,0..5]')
		self.assertIsInstance(array1d, ArrayType)
		self.assertIsInstance(array2d, ArrayType)
		self._test_conflict_both_ways(array1d, array2d)
	
	def test_array_incompatible_with_array_of_same_type_and_different_bounds(self):
		array1 = self.analyze('array_type', 'tableau entier[0..1]')
		array2 = self.analyze('array_type', 'tableau entier[0..2]')
		array3 = self.analyze('array_type', 'tableau entier[-1..1]')
		array4 = self.analyze('array_type', 'tableau entier[-1..2]')
		self.assertIsInstance(array1, ArrayType)
		self.assertIsInstance(array2, ArrayType)
		self.assertIsInstance(array3, ArrayType)
		self.assertIsInstance(array4, ArrayType)
		self._test_conflict_both_ways(array1, array2)
		self._test_conflict_both_ways(array1, array3)
		self._test_conflict_both_ways(array1, array4)

	def test_array_incompatible_with_array_of_different_type_and_same_dimensions(self):
		int_array = self.analyze('array_type', 'tableau entier[0..5]')
		real_array = self.analyze('array_type', 'tableau réel[0..5]')
		self.assertIsInstance(int_array, ArrayType)
		self.assertIsInstance(real_array, ArrayType)
		self._test_conflict_both_ways(int_array, real_array)

