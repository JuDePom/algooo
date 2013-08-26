from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.statements import If
from lda.module import Algorithm

class TestIfSemantics(LDATestCase):
	def test_if_literal_boolean_condition(self):
		self.check(cls=If, program="si vrai alors fsi")
		self.check(cls=If, program="si faux alors fsi")

	def test_if_boolean_expression_condition(self):
		self.check(cls=If, program="si 1+1=2 alors fsi")

	def test_if_non_boolean_condition(self):
		def test(raw_condition):
			program = '''\
				algorithme
				lexique
					Moule = <>
					en: entier
					re: réel
					ch: chaîne
					ca: caractère
					m: Moule
				début
					si (**){} alors fsi
				fin'''.format(raw_condition)
			self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
					program=program)
		test('1234')
		test('123.456')
		test('"les poules ont des dents"')
		test("'a'")
		test('en')
		test('re')
		test('ch')
		test('ca')
		test('m')

