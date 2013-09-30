from tests.ldatestcase import LDATestCase

class TestJSStatements(LDATestCase):
	def test_for_iteration_count(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
				début
					pour i de 1 jusque 10 faire
						écrire(i)
					fpour
				fin"""))

	def test_while_iteration_count(self):
		self.assertEqual("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", self.jseval(program="""\
				algorithme
				lexique
					i: entier
				début
					i <- 1
					tantque i <= 10 faire
						écrire(i)
						i <- i + 1
					ftant
				fin"""))

	def test_if_then_elif_else(self):
		self.assertEqual("-\n+\n0\n", self.jseval(program="""\
				fonction f(x: entier)
				lexique x: entier
				début
					si x < 0 alors
						écrire("-")
					snsi x > 0 alors
						écrire("+")
					sinon
						écrire("0")
					fsi
				fin

				algorithme
				début
					f(-100)
					f(+100)
					f(0)
				fin"""))
