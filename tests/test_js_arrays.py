from tests.ldatestcase import LDATestCase

class TestJSArrays(LDATestCase):
	def test_1d_static_integer_array_assignments(self):
		output = '\n'.join(str(i) for i in range(100, 110)) + '\n'
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					i: entier
					t: tableau entier[1..10]
				début
					pour i de 1 jusque 10 faire
						t[i] <- 100 + i - 1
					fpour
					pour i de 1 jusque 10 faire
						écrire(t[i])
					fpour
				fin"""))

	def test_2d_static_integer_array_assignments(self):
		output = '\n'.join(str(i) for i in range(1, 51)) + '\n'
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					c: entier
					i: entier
					j: entier
					t: tableau entier[1..10, 1..5]
				début
					c <- 1
					pour i de 1 à 10 faire
						pour j de 1 à 5 faire
							t[i, j] <- c
							c <- c + 1
						fpour
					fpour
					pour i de 1 à 10 faire
						pour j de 1 à 5 faire
							écrire(t[i, j])
						fpour
					fpour
				fin"""))

