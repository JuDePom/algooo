from tests import ldatestcase

class TestJSPassByCopy(ldatestcase.LDATestCase):
	def _scalar_pbc(self, ldatype, tempval, finalval, expected_output):
		self.assertEqual(expected_output, self.jseval(program="""\
				fonction f(a: {ldatype})
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

