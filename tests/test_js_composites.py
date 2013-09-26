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


	def test_1d_static_array_of_composites(self):
		# Composites are interesting because they require a special `filler` in
		# the Array constructor.
		output = '\n'.join(str(i) for i in range(1, 11)) + '\n'
		self.assertEqual(output, self.jseval(program="""\
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
		output = '100\n' * 100
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					i: entier
					j: entier
					Moule = <a: entier>
					t: tableau Moule[1..10, 1..10]
				début
					pour i de 1 jusque 10 faire
						pour j de 1 jusque 10 faire
							t[i,j].a <- 100
						fpour
					fpour
					pour i de 1 jusque 10 faire
						pour j de 1 jusque 10 faire
							écrire(t[i,j].a)
						fpour
					fpour
				fin"""))

	def test_complex_weave_of_composites_and_1d_dynamic_arrays(self):
		palme = ("palme\n"*i for i in range(1, 51))
		output = ''.join("{}\n{}".format(number, string)
				for number, string in zip(range(1,51), palme))
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					Moule = <viscosité: entier, tabfrites: tableau Frite[?]>
					Frite = <huile: chaîne>
					tabdélice: tableau Moule[?]
					i: entier
					j: entier
				début
					tailletab(tabdélice, 1..50)
					pour i de 1 à 50 faire
						tabdélice[i].viscosité <- i
						tailletab(tabdélice[i].tabfrites, 1..i)
						pour j de 1 à i faire
							tabdélice[i].tabfrites[j].huile <- "palme"
						fpour
					fpour
					pour i de 1 à 50 faire
						écrire(tabdélice[i].viscosité)
						pour j de 1 à i faire
							écrire(tabdélice[i].tabfrites[j].huile)
						fpour
					fpour
				fin"""))


