from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestIfSemantics(LDATestCase):
	def test_if_non_boolean_condition(self):
		def test(raw_condition):
			program = '''algorithme
				lexique
					Moule = <>
					en: entier
					re: réel
					ch: chaîne
					ca: caractère
					m: Moule
				début
					si {} alors fsi
				fin'''.format(raw_condition)
			self.assertRaises(semantic.SemanticError, self.check, 'module', program)
		test('1234')
		test('123.456')
		test('"les poules ont des dents"')
		test("'a'")
		test('en')
		test('re')
		test('ch')
		test('ca')
		test('m')

