from tests.ldatestcase import LDATestCase
from lda.operators import FunctionCall, MemberSelect
from lda.statements import If, StatementBlock
from lda.errors import syntax
from lda import kw

class TestIfSyntax(LDATestCase):
	def test_if_then(self):
		stmt = self.analyze(cls=If,
				program="si toto.gentil alors bisou(toto) fsi")
		self.assertIsInstance(stmt.conditionals[0].condition, MemberSelect)
		self.assertIsInstance(stmt.conditionals[0].body, list)
		self.assertIsNone(stmt.else_block)

	def test_if_then_else(self):
		stmt = self.analyze(cls=If,
				program="si toto.gentil alors bisou(toto) sinon fessée(toto) fsi")
		self.assertIsInstance(stmt.conditionals[0].condition, MemberSelect)
		self.assertIsInstance(stmt.conditionals[0].body, list)
		self.assertIsInstance(stmt.else_block, StatementBlock)

	def test_if_nested_within_else(self):
		stmt = self.analyze(cls=If,
				program="""\
				si x alors y()
				sinon
					si z alors w() fsi
				fsi""")
		self.assertIsInstance(stmt.else_block.body[0], If)

	def test_multiple_elifs_single_endif(self):
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

	def test_multiple_elses(self):
		stmt = self.assertMissingKeywords(kw.END_IF, cls=If,
				program="""\
				si x alors y()
				sinon z()
				(**)sinon w()
				fsi""")

	def test_if_missing_keyword(self):
		def test(p, *args):
			self.assertMissingKeywords(*args, cls=If, program=p)
		test("si toto.gentil(**)bisou(toto) fsi", kw.THEN)
		test("si toto.gentil alors bisou(toto)(**)", kw.END_IF, kw.ELSE, kw.ELIF)
		test("si toto.gentil alors bisou(toto) sinon fessée(toto)(**)", kw.END_IF)

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

