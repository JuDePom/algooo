from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestBuiltinArrayAlloc(LDATestCase):
	def test_non_array(self):
		self.assertLDAError(semantic.TypeError, analyzer=self.check, program="""\
				algorithme
				lexique
					t: chaîne
				début
					tailletab((**)t, 0..5)
				fin""")

	def test_static_array(self):
		self.assertLDAError(semantic.TypeError, analyzer=self.check, program="""\
				algorithme
				lexique
					t: tableau entier[0..5]
				début
					tailletab((**)t, 0..5)
				fin""")

	def test_too_few_dimensions(self):
		self.assertLDAError(semantic.DimensionCountMismatch, analyzer=self.check,
				program="""\
				algorithme
				lexique
					t: tableau entier[?, ?, ?]
				début
					tailletab((**)t, 0..5, 0..5)
				fin""")

	def test_too_many_dimensions(self):
		self.assertLDAError(semantic.DimensionCountMismatch, analyzer=self.check,
				program="""\
				algorithme
				lexique
					t: tableau entier[?, ?, ?]
				début
					tailletab((**)t, 0..5, 0..5, 0..5, 0..5)
				fin""")

	def test_0_dimensions(self):
		self.assertLDAError(semantic.ParameterCountMismatch, analyzer=self.check,
				program="""\
				algorithme
				lexique
					t: tableau entier[?, ?, ?]
				début
					(**)tailletab(t)
				fin""")

	def test_0_parameters(self):
		self.assertLDAError(semantic.ParameterCountMismatch, analyzer=self.check,
				program="algorithme début (**)tailletab() fin")

	def test_try_initializing_sub_array(self):
		# This test is somewhat redundant because this case is not handled
		# directly by arrayalloc; the ArraySubscript operator makes sure this
		# is semantically impossible. In any case, it should fail.
		self.assertLDAError(semantic.DimensionCountMismatch, analyzer=self.check,
				program="""\
				algorithme
				lexique
					t: tableau entier[?, ?]
				début
					tailletab(t, 0..5, 0..5)
					tailletab(t(**)[0], 10..12)
				fin""")

