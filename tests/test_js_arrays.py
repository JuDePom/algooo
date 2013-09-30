from tests.ldatestcase import LDATestCase
from subprocess import CalledProcessError

class TestJSArrays(LDATestCase):
	def test_1d_static_integer_array_assignments(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
					t: tableau entier[101..110]
				début
					pour i de 101 jusque 110 faire
						t[i] <- i - 100
					fpour
					pour i de 101 jusque 110 faire
						écrire(t[i])
					fpour
				fin"""))

	def test_1d_static_integer_array_access_out_of_bounds(self):
		self.assertRaises(CalledProcessError, self.jseval, shutup=True, program="""\
				algorithme
				lexique
					t: tableau entier[1..10]
				début
					t[-999] <- 3
				fin""")

	def test_2d_static_integer_array_assignments(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					c: entier
					i: entier
					j: entier
					t: tableau entier[0..1, 1..5]
				début
					pour i de 0 à 1 faire
						pour j de 1 à 5 faire
							t[i, j] <- i * 5 + j
						fpour
					fpour
					pour i de 0 à 1 faire
						pour j de 1 à 5 faire
							écrire(t[i, j])
						fpour
					fpour
				fin"""))

	def test_1d_dynamic_integer_array_assignments_and_retrievals(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
					t: tableau entier[?]
				début
					tailletab(t, 101..110)
					pour i de 101 jusque 110 faire
						t[i] <- i - 100
					fpour
					pour i de 101 jusque 110 faire
						écrire(t[i])
					fpour
				fin"""))

	def test_2d_dynamic_integer_array_assignments_and_retrievals(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
					j: entier
					t: tableau entier[?, ?]
				début
					tailletab(t, 0..1, 1..5)
					pour i de 0 jusque 1 faire
						pour j de 1 jusque 5 faire
							t[i, j] <- i * 5 + j
						fpour
					fpour
					pour i de 0 jusque 1 faire
						pour j de 1 jusque 5 faire
							écrire(t[i, j])
						fpour
					fpour
				fin"""))

	def test_2d_dynamic_integer_array_access_out_of_bounds(self):
		self.assertRaises(CalledProcessError, self.jseval, shutup=True, program="""\
				algorithme
				lexique
					t: tableau entier[?]
				début
					tailletab(t, 100..110)
					t[-999] <- 30
				fin""")

