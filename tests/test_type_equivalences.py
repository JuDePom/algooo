from tests.ldatestcase import LDATestCase
from lda import types
from lda.errors import semantic
from lda.identifier import PureIdentifier
from lda.operators import LogicalOr

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
		self._test_self_compatibility(types.INTEGER)

	def test_integer_weaker_than_real(self):
		self._test_compatibility_both_ways(types.INTEGER, types.REAL)

	def test_character_weaker_than_string(self):
		self._test_compatibility_both_ways(types.CHARACTER, types.STRING)

	def test_integer_incompatible_with_non_numbers(self):
		self._test_conflict_both_ways(types.INTEGER, types.STRING)
		self._test_conflict_both_ways(types.INTEGER, types.CHARACTER)
		self._test_conflict_both_ways(types.INTEGER, types.BOOLEAN)
		self._test_conflict_both_ways(types.INTEGER,
				self.analyze(cls=types.Array, program="tableau entier[0..5]"))
		self._test_conflict_both_ways(types.INTEGER,
				self.analyze(cls=types.Composite, program="<a: entier>", ident=None))

	def test_real_incompatible_with_non_numbers(self):
		self._test_conflict_both_ways(types.REAL, types.STRING)
		self._test_conflict_both_ways(types.REAL, types.CHARACTER)
		self._test_conflict_both_ways(types.REAL, types.BOOLEAN)
		self._test_conflict_both_ways(types.REAL,
				self.analyze(cls=types.Array, program="tableau réel[0..5]"))
		self._test_conflict_both_ways(types.REAL,
				self.analyze(cls=types.Composite, program="<a: réel>", ident=None))

	def test_string_incompatible_with_composite_and_array(self):
		self._test_conflict_both_ways(types.STRING,
				self.analyze(cls=types.Array, program="tableau caractère[0..5]"))
		self._test_conflict_both_ways(types.STRING,
				self.analyze(cls=types.Composite, program="<a: chaîne>", ident=None))

	def test_composite_compatible_with_itself(self):
		moule1 = self.analyze(cls=types.Composite, program="<>", ident=PureIdentifier(None, "Moule"))
		moule2 = self.analyze(cls=types.Composite, program="<>", ident=PureIdentifier(None, "Moule"))
		self._test_compatibility_both_ways(moule1, moule1)
		self._test_compatibility_both_ways(moule1, moule2)

	def test_composite_incompatible_with_other_composite_with_different_identifier(self):
		moule1 = self.analyze(cls=types.Composite, program="<>", ident=PureIdentifier(None, "Moule1"))
		moule2 = self.analyze(cls=types.Composite, program="<>", ident=PureIdentifier(None, "Moule2"))
		self._test_conflict_both_ways(moule1, moule2)

	def test_1d_static_array_compatible_with_itself(self):
		array = self.analyze(cls=types.Array, program="tableau entier[0..5]")
		self._test_self_compatibility(array)

	def test_2d_static_array_compatible_with_itself(self):
		array = self.analyze(cls=types.Array, program="tableau entier[0..5, -1337..1337]")
		self._test_self_compatibility(array)

	def test_1d_static_array_incompatible_with_2d_static_array(self):
		array1d = self.analyze(cls=types.Array, program="tableau entier[0..5]")
		array2d = self.analyze(cls=types.Array, program="tableau entier[0..5,0..5]")
		self._test_conflict_both_ways(array1d, array2d)

	def test_1d_static_array_incompatible_with_1d_static_array_with_other_bounds(self):
		array1 = self.analyze(cls=types.Array, program="tableau entier[0..1]")
		array2 = self.analyze(cls=types.Array, program="tableau entier[0..2]")
		array3 = self.analyze(cls=types.Array, program="tableau entier[-1..1]")
		array4 = self.analyze(cls=types.Array, program="tableau entier[-1..2]")
		self._test_conflict_both_ways(array1, array2)
		self._test_conflict_both_ways(array1, array3)
		self._test_conflict_both_ways(array1, array4)

	def test_1d_static_array_incompatible_with_1d_array_of_different_type_and_same_bounds(self):
		int_array  = self.analyze(cls=types.Array, program="tableau entier[0..5]")
		real_array = self.analyze(cls=types.Array, program="tableau réel[0..5]")
		self._test_conflict_both_ways(int_array, real_array)

	def test_1d_dynamic_array_compatible_with_itself(self):
		array = self.analyze(cls=types.Array, program="tableau entier[?]")
		self._test_self_compatibility(array)

	def test_1d_dynamic_array_compatible_with_other_1d_dynamic_array(self):
		array1 = self.analyze(cls=types.Array, program="tableau entier[?]")
		array2 = self.analyze(cls=types.Array, program="tableau entier[?]")
		self._test_compatibility_both_ways(array1, array2)

	def test_2d_half_dynamic_half_static_array_compatible_with_itself(self):
		array = self.analyze(cls=types.Array, program="tableau entier[?, 0..5]")
		self._test_self_compatibility(array)

	def test_2d_half_dynamic_half_static_array_compatible_with_other_such_array(self):
		array1 = self.analyze(cls=types.Array, program="tableau entier[?, 0..5]")
		array2 = self.analyze(cls=types.Array, program="tableau entier[?, 0..5]")
		self._test_compatibility_both_ways(array1, array2)

	def test_pass_real_to_function_expecting_integer(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, program="""\
				fonction f(a: entier)
				lexique
					a: entier
				début
					f((**)3.00)
				fin""")

	def test_pass_integer_to_function_expecting_real(self):
		self.check(program="""\
				fonction f(a: réel)
				lexique
					a: réel
				début
					f(3)
				fin""")

	def test_pass_good_1d_static_array_to_function(self):
		self.check(program="""\
				fonction f(t: tableau entier[0..5])
				lexique
					t: tableau entier[0..5]
				début fin

				algorithme
				lexique
					t: tableau entier[0..5]
				début
					f(t)
				fin""")

	def test_pass_bad_1d_static_array_to_function(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				fonction f(t: tableau entier[0..5])
				lexique
					t: tableau entier[0..5]
				début fin

				algorithme
				lexique
					t: tableau entier[1..5]
				début
					f((**)t)
				fin""")

	def test_assign_integer_literal_to_real(self):
		self.check(program="""\
				algorithme
				lexique r:réel
				début r<-3 fin""")

	def test_assign_integer_variable_to_real(self):
		self.check(program="""\
				algorithme
				lexique
					r: réel
					e: entier
				début
					e <- 3
					r <- e
				fin""")

	def test_assign_real_literal_to_integer(self):
		self.assertLDAError(semantic.TypeMismatch, self.check,
				program="""algorithme
				lexique e:entier
				début e(**)<-3.00000 fin""")

	def test_assign_real_variable_to_integer(self):
		self.assertLDAError(semantic.TypeMismatch, self.check,
				program="""algorithme
				lexique r:réel e:entier
				début r<-3.00000  e(**)<-r  fin""")

	def test_assign_integer_to_inout_integer(self):
		self.check(program="""\
				fonction f(a: inout entier)
				lexique
					a: inout entier
				début
					a <- 3
				fin""")

	def test_assign_integer_to_inout_real(self):
		self.check(program="""\
				fonction f(a: inout réel)
				lexique
					a: inout réel
				début
					a <- 3
				fin""")

	def test_assign_function_to_integer(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
				fonction f(): entier
				lexique
					a: entier
				début
					a (**)<- f
					retourne a
				fin""")

	def test_arithmetic_with_inout_integer(self):
		self.check(program="""\
				fonction f(a: inout entier)
				lexique a: inout entier    b: entier
				début b <- a * 2 fin""")

	def test_assign_inout_integer_to_plain_integer(self):
		self.check(program="""\
				fonction f(a: inout entier)
				lexique a: inout entier   b : entier
				début b <- a fin""")

	def test_assign_plain_integer_to_inout_integer(self):
		self.check(program="""\
				fonction f(a: inout entier)
				lexique a: inout entier   b : entier
				début a <- b fin""")

	def test_binary_logical_op_with_binary_operands(self):
		self.check(cls=LogicalOr, program="vrai ou faux")
		self.check(cls=LogicalOr, program="vrai ou vrai")
		self.check(cls=LogicalOr, program="faux ou vrai")
		self.check(cls=LogicalOr, program="faux ou faux")

	def test_binary_logical_op_with_non_binary_operands(self):
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program="vrai ou (**)3")
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program="(**)3 ou vrai")
		self.assertLDAError(semantic.SpecificTypeExpected, self.check, cls=LogicalOr,
				program="(**)3 ou (**)4")

