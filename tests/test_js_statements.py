from tests.ldatestcase import LDATestCase

class TestJSStatements(LDATestCase):
	def test_for_iteration_count(self):
		output = '\n'.join(str(i) for i in range(1, 11)) + '\n'
		self.assertEqual(output, self.jseval(program="""\
				algorithme
				lexique
					i: entier
				début
					pour i de 1 jusque 10 faire
						écrire(i)
					fpour
				fin"""))

