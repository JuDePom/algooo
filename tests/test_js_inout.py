from . import ldatestcase

class TestJSInout(ldatestcase.LDATestCase):
	def _scalar_inout(self, ldatype, tempval, finalval, expected_output):
		self.assertEqual(expected_output, self.jseval(program="""\
				fonction f(a: inout {ldatype})
				lexique
					a: inout {ldatype}
				début
					a <- {finalval}
				fin

				algorithme
				lexique
					a: {ldatype}
				début
					a <- {tempval}
					f(a)
					écrire(a)
				fin""".format(ldatype=ldatype, tempval=tempval, finalval=finalval)))

	def test_pass_integer_by_inout(self):
		self._scalar_inout("entier", "1234", "1000", "1000\n")

	def test_pass_real_by_inout(self):
		self._scalar_inout("réel", "12.34", "3.1416", "3.1416\n")

	def test_pass_string_by_inout(self):
		self._scalar_inout("chaîne", '"remplacement"', '"original"', "original\n")

	def test_pass_character_by_inout(self):
		self._scalar_inout("caractère", "'R'", "'O'", "O\n")

