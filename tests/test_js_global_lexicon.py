from tests.ldatestcase import LDATestCase

class TestJSGlobalLexicon(LDATestCase):
	def test_create_local_variable_from_global_composite(self):
		self.assertEqual("123\nhejsan\n", self.jseval(program="""\
				lexique
					Moule = <a: entier, b: chaîne>

				algorithme
				lexique
					m: Moule
				début
					m.a <- 123
					m.b <- "hejsan"
					écrire(m.a)
					écrire(m.b)
				fin"""))
				
	def test_modify_global_variable_in_three_different_places(self):
		self.assertEqual("42\n", self.jseval(program="""\
				lexique
					globale: entier

				fonction ajouter3()
				début globale <- globale + 3 fin

				fonction doubler()
				début globale <- globale * 2 fin

				algorithme
				début
					globale <- 6
					ajouter3()
					doubler()
					doubler()
					ajouter3()
					ajouter3()
					écrire(globale)
				fin"""))

