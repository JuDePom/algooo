from tests.ldatestcase import LDATestCase

class TestJSExpressions(LDATestCase):
	def test_simple_member_select(self):
		self.assertEqual("2\n3.141593\n", self.jseval(program="""\
				algorithme
				lexique
					Moule = <a: entier, b: réel>
					a: Moule
				début
					a.a <- 1 + 1
					a.b <- 0.10109 + .000503 + .04 + 1.0000 * 9. / 3.
					écrire(a.a)
					écrire(a.b)
				fin"""))

	def test_cross_referenced_composite(self):
		self.assertEqual("0.96\ntournesol\n", self.jseval(program="""\
				algorithme
				lexique
					Moule = <viscosité: réel, f: Frite>
					Frite = <huile: chaîne>
					délicieux: Moule
				début
					délicieux.viscosité <- .96
					délicieux.f.huile <- "tournesol"
					écrire(délicieux.viscosité)
					écrire(délicieux.f.huile)
				fin"""))

	def test_array_member_in_composite(self):
		output = '\n'.join(str(i) for i in range(1, 11)) + '\n'
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					i: entier
					Moule = <t: tableau entier[1..10]>
					m: Moule
				début
					pour i de 1 jusque 10 faire
						m.t[i] <- i
					fpour
					pour i de 1 jusque 10 faire
						écrire(m.t[i])
					fpour
				fin"""))


