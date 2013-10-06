from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.statements import For

class TestForSemantics(LDATestCase):

	def test_for_literal_counter(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=For,
				program='pour (**)0 de 1 jusque 6 faire fpour')

	def test_for_non_integer_counter(self):
		def test(raw_counter_type):
			program = '''algorithme
					lexique
						Moule = <>
						a: {}
					début
						pour (**)a de 1 jusque 5 faire fpour
					fin'''.format(raw_counter_type)
			self.assertLDAError(semantic.SemanticError, self.check, program=program)
		test('chaîne')
		test('réel')
		test('caractère')
		test('booléen')
		test('Moule')

	def test_for_non_integer_initial_and_final(self):
		def test(raw_initial, raw_final):
			program = '''algorithme
					lexique
						Moule = <>
						i: entier
						m: Moule
						ch: chaîne
						re: réel
						bo: booléen
					début
						pour i de {} jusque {} faire fpour
					fin'''.format(raw_initial, raw_final)
			self.assertLDAError(semantic.SemanticError, self.check, program=program)
		test('(**)"abc"', '5')
		test('(**)vrai', '5')
		test('(**)1.234', '5')
		test("(**)'a'", '5')
		test('5', '(**)"abc"')
		test('5', '(**)vrai')
		test('5', '(**)6.789')
		test('5', "(**)'a'")
		test('(**)"abc"', '(**)"def"')
		test('(**)m', '0')
		test('(**)ch', '0')
		test('(**)re', '0')
		test('(**)bo', '0')
		test('0', '(**)m')
		test('0', '(**)ch')
		test('0', '(**)re')
		test('0', '(**)bo')

