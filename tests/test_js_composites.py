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
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
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


	def test_1d_static_array_of_composites(self):
		# Composites are interesting because they require a special `filler` in
		# the Array constructor.
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
					Moule = <a: entier>
					t: tableau Moule[1..10]
				début
					pour i de 1 jusque 10 faire
						t[i].a <- i
					fpour
					pour i de 1 jusque 10 faire
						écrire(t[i].a)
					fpour
				fin"""))

	def test_2d_static_array_of_composites(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
					j: entier
					Moule = <a: entier>
					t: tableau Moule[1..5, 1..2]
				début
					pour i de 1 jusque 5 faire
						pour j de 1 jusque 2 faire
							t[i, j].a <- (i - 1) * 2 + j
						fpour
					fpour
					pour i de 1 jusque 5 faire
						pour j de 1 jusque 2 faire
							écrire(t[i, j].a)
						fpour
					fpour
				fin"""))

	def test_complex_weave_of_composites_and_1d_dynamic_arrays(self):
		self.assertEqual("1\npalme\n2\npalme\npalme\n3\npalme\npalme\npalme\n", self.jseval(program="""\
				algorithme
				lexique
					Moule = <viscosité: entier, tabfrites: tableau Frite[?]>
					Frite = <huile: chaîne>
					tabdélice: tableau Moule[?]
					i: entier
					j: entier
				début
					tailletab(tabdélice, 1..3)
					pour i de 1 à 3 faire
						tabdélice[i].viscosité <- i
						tailletab(tabdélice[i].tabfrites, 1..i)
						pour j de 1 à i faire
							tabdélice[i].tabfrites[j].huile <- "palme"
						fpour
					fpour
					pour i de 1 à 3 faire
						écrire(tabdélice[i].viscosité)
						pour j de 1 à i faire
							écrire(tabdélice[i].tabfrites[j].huile)
						fpour
					fpour
				fin"""))


