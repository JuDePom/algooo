from tests.ldatestcase import LDATestCase
from lda.operators import FunctionCall, MemberSelect
from lda.statements import If, StatementBlock
from lda.errors import syntax

class TestIfSyntax(LDATestCase):
	def test_if_then(self):
		stmt = self.analyze(cls=If,
				program="si toto.gentil alors bisou(toto) fsi")
		self.assertIsInstance(stmt.conditionals[0].condition, MemberSelect)
		self.assertIsInstance(stmt.conditionals[0].block, StatementBlock)
		self.assertIsNone(stmt.else_block)

	def test_if_then_else(self):
		stmt = self.analyze(cls=If,
				program="si toto.gentil alors bisou(toto) sinon fessée(toto) fsi")
		self.assertIsInstance(stmt.conditionals[0].condition, MemberSelect)
		self.assertIsInstance(stmt.conditionals[0].block, StatementBlock)
		self.assertIsInstance(stmt.else_block, StatementBlock)

	def test_nested_ifs_single_endif(self):
		stmt = self.analyze(cls=If, program='''\
			si toto.gentil alors
				bisou(toto)
			snsi toto.triste alors
				nourrir(toto)
			snsi toto.age < 5 alors
				au_coin(toto)
			sinon
				fessée(toto)
			fsi''')
		self.assertEqual(3, len(stmt.conditionals))
		self.assertIsNotNone(stmt.else_block)

	def test_if_missing_keyword(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedKeyword, self.analyze, cls=If, program=p)
		test("si toto.gentil(**)bisou(toto) fsi")
		test("si toto.gentil alors bisou(toto)(**)")
		test("si toto.gentil alors bisou(toto) sinon fessée(toto)(**)")
	
	def test_if_then_without_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=If,
				program='si (**)alors fsi')

	def test_if_with_assignment_as_condition(self):
		self.assertLDAError(syntax.SyntaxError, self.check, program="""\
					algorithme
					lexique
						a: entier
					début
						si a (**)<- 3 alors
						fsi
					fin""")

