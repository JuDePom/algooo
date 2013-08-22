from tests.ldatestcase import LDATestCase
from lda.operators import FunctionCall, MemberSelect
from lda.statements import IfThenElse, StatementBlock
from lda.errors import syntax

class TestIfSyntax(LDATestCase):
	def test_if_then(self):
		stmt = self.analyze(IfThenElse, "si toto.gentil alors bisou(toto) fsi")
		self.assertIsInstance(stmt.condition, MemberSelect)
		self.assertIsInstance(stmt.then_block, StatementBlock)
		self.assertIs(stmt.else_block, None)

	def test_if_then_else(self):
		stmt = self.analyze(IfThenElse, "si toto.gentil alors bisou(toto) sinon fessée(toto) fsi")
		self.assertIsInstance(stmt.condition, MemberSelect)
		self.assertIsInstance(stmt.then_block, StatementBlock)
		self.assertIsInstance(stmt.else_block, StatementBlock)
	
	def test_nested_ifs_single_endif(self):
		stmt = self.analyze(IfThenElse, '''\
			si toto.gentil alors
				bisou(toto)
			sinon si toto.triste alors
				nourrir(toto)
			sinon si toto.age < 5 alors
				au_coin(toto)
			sinon
				fessée(toto)
			fsi''')
		# !gentil, triste?
		self.assertIsInstance(stmt.statements.else_block, statements.IfThenElse)
		# !gentil, !triste, age<5?
		self.assertIsInstance(stmt.statements.else_block.else_block, IfThenElse)
		# !gentil, !triste, !(age<5)
		self.assertIsInstance(stmt.statements.else_block.else_block.else_block, FunctionCall)

	def test_if_missing_keyword(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedKeyword, self.analyze, cls=IfThenElse, program=p)
		test("si toto.gentil(**)bisou(toto) fsi")
		test("si toto.gentil alors bisou(toto)(**)")
		test("si toto.gentil alors bisou(toto) sinon fessée(toto)(**)")
	
	def test_if_then_without_condition(self):
		self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=IfThenElse,
				program='si (**)alors fsi')

