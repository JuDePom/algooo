from . import ldatestcase

class TestJSPassByCopy(ldatestcase.LDATestCase):
	def _scalar_pbc(self, ldatype, tempval, finalval, expected_output):
		self.assertEqual(expected_output, self.jseval(program="""\
				fonction f(a: {ldatype})
				lexique
					a: {ldatype}
				début
					a <- {tempval}
				fin

				algorithme
				lexique
					a: {ldatype}
				début
					a <- {finalval}
					f(a)
					écrire(a)
				fin""".format(ldatype=ldatype, tempval=tempval, finalval=finalval)))

	def test_pass_integer_by_copy(self):
		self._scalar_pbc("entier", "1234", "1000", "1000\n")

	def test_pass_real_by_copy(self):
		self._scalar_pbc("réel", "12.34", "3.1416", "3.1416\n")

	def test_pass_string_by_copy(self):
		self._scalar_pbc("chaîne", '"remplacement"', '"original"', "original\n")

	def test_pass_character_by_copy(self):
		self._scalar_pbc("caractère", "'R'", "'O'", "O\n")

	def test_pass_array_by_copy(self):
		self.assertEqual("original\n", self.jseval(program="""\
				fonction f(t: tableau chaîne[0..9])
				lexique
					t: tableau chaîne[0..9]
				début
					t[5] <- "remplacement"
				fin

				algorithme
				lexique
					t: tableau chaîne[0..9]
				début
					t[5] <- "original"
					f(t)
					écrire(t[5])
				fin"""))

	def test_pass_composite_by_copy(self):
		self.assertEqual("original\n", self.jseval(program="""\
				lexique
					Moule = <a: chaîne>

				fonction f(m: Moule)
				lexique
					m: Moule
				début
					m.a <- "remplacement"
				fin

				algorithme
				lexique
					m: Moule
				début
					m.a <- "original"
					f(m)
					écrire(m.a)
				fin"""))

