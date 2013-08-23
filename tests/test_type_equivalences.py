from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.typedesc import *
from lda.operators import LogicalOr
from lda.module import Module, Algorithm

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
		self._test_conflict_both_ways(Integer, self.analyze(ArrayType, 'tableau entier[0..5]'))
		self._test_conflict_both_ways(Integer, self.analyze(CompositeType, 'Moule = <a: entier>'))

	def test_real_incompatible_with_non_numbers(self):
		self._test_conflict_both_ways(Real, String)
		self._test_conflict_both_ways(Real, Character)
		self._test_conflict_both_ways(Real, Boolean)
		self._test_conflict_both_ways(Real, self.analyze(ArrayType, 'tableau réel[0..5]'))
		self._test_conflict_both_ways(Real, self.analyze(CompositeType, 'Moule = <a: réel>'))

	def test_string_incompatible_with_composite_and_array(self):
		self._test_conflict_both_ways(String, self.analyze(ArrayType, 'tableau caractère[0..5]'))
		self._test_conflict_both_ways(String, self.analyze(CompositeType, 'Moule = <a: chaîne>'))

	def test_composite_compatible_with_itself(self):
		moule1 = self.analyze(CompositeType, 'Moule = <>')
		moule2 = self.analyze(CompositeType, 'Moule = <>')
		self._test_compatibility_both_ways(moule1, moule1)
		self._test_compatibility_both_ways(moule1, moule2)

	def test_composite_incompatible_with_other_composite_with_different_identifier(self):
		moule1 = self.analyze(CompositeType, 'Moule1 = <>')
		moule2 = self.analyze(CompositeType, 'Moule2 = <>')
		self._test_conflict_both_ways(moule1, moule2)

	def test_array_compatible_with_itself(self):
		array = self.analyze(ArrayType, 'tableau entier[0..5]')
		self._test_self_compatibility(array)

	def test_array_incompatible_with_array_of_same_type_and_different_dimensions(self):
		array1d = self.analyze(ArrayType, 'tableau entier[0..5]')
		array2d = self.analyze(ArrayType, 'tableau entier[0..5,0..5]')
		self._test_conflict_both_ways(array1d, array2d)

	def test_array_incompatible_with_array_of_same_type_and_different_bounds(self):
		array1 = self.analyze(ArrayType, 'tableau entier[0..1]')
		array2 = self.analyze(ArrayType, 'tableau entier[0..2]')
		array3 = self.analyze(ArrayType, 'tableau entier[-1..1]')
		array4 = self.analyze(ArrayType, 'tableau entier[-1..2]')
		self._test_conflict_both_ways(array1, array2)
		self._test_conflict_both_ways(array1, array3)
		self._test_conflict_both_ways(array1, array4)

	def test_array_incompatible_with_array_of_different_type_and_same_dimensions(self):
		int_array  = self.analyze(ArrayType, 'tableau entier[0..5]')
		real_array = self.analyze(ArrayType, 'tableau réel[0..5]')
		self._test_conflict_both_ways(int_array, real_array)

	def test_pass_real_to_function_expecting_integer(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=Module, program='''\
				fonction f(a: entier)
				lexique
					a: entier
				début
					f((**)3.00)
				fin''')

	def test_pass_integer_to_function_expecting_real(self):
		self.check(cls=Module, program='''\
				fonction f(a: réel)
				lexique
					a: réel
				début
					f(3)
				fin''')

	def test_assign_integer_literal_to_real(self):
		self.check(cls=Algorithm, program='''\
				algorithme
				lexique r:réel
				début r<-3 fin''')

	def test_assign_integer_variable_to_real(self):
		self.check(cls=Algorithm, program='''\
				algorithme
				lexique r:réel e:entier
				début e<-3   r<-e fin''')

	def test_assign_real_literal_to_integer(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, cls=Algorithm,
				program='''algorithme
				lexique e:entier
				début e<-(**)3.00000 fin''')

	def test_assign_real_variable_to_integer(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, cls=Algorithm,
				program='''algorithme
				lexique r:réel e:entier
				début r<-3.00000  e<-(**)r  fin''')

	def test_binary_logical_op_with_binary_operands(self):
		self.check(cls=LogicalOr, program='vrai ou faux')
		self.check(cls=LogicalOr, program='vrai ou vrai')
		self.check(cls=LogicalOr, program='faux ou vrai')
		self.check(cls=LogicalOr, program='faux ou faux')

	def test_binary_logical_op_with_non_binary_operands(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program='vrai ou (**)3')
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program='(**)3 ou vrai')
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program='(**)3 ou (**)4')

