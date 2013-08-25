from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.statements import While
from lda.module import Algorithm

class TestWhileSemantics(LDATestCase):
	def test_while_literal_boolean_condition(self):
		self.check(cls=While, program="tantque vrai faire ftant")
		self.check(cls=While, program="tantque faux faire ftant")

	def test_while_boolean_expression_condition(self):
		self.check(cls=While, program="tantque 1+1=2 faire ftant")

	def test_while_non_boolean_condition(self):
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
						tantque (**){} faire ftant
					fin'''.format(raw_condition)
			self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm, program=program)
		test('1234')
		test('123.456')
		test('"les poules ont des dents"')
		test("'a'")
		test('en')
		test('re')
		test('ch')
		test('ca')
		test('m')

