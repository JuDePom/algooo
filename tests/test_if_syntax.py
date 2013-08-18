from tests.ldatestcase import LDATestCase
from lda import expression
from lda import operators
from lda import statements
from lda.errors import syntax

class TestIfSyntax(LDATestCase):
	def test_if_then(self):
		stmt = self.analyze("if", "si toto.gentil alors bisou(toto) fsi")
		self.assertIsInstance(stmt, statements.IfThenElse)
		self.assertIsInstance(stmt.condition, operators.MemberSelect)
		self.assertIsInstance(stmt.then_block, statements.StatementBlock)
		self.assertIs(stmt.else_block, None)

	def test_if_then_else(self):
		stmt = self.analyze("if", "si toto.gentil alors bisou(toto) sinon fessée(toto) fsi")
		self.assertIsInstance(stmt, statements.IfThenElse)
		self.assertIsInstance(stmt.condition, operators.MemberSelect)
		self.assertIsInstance(stmt.then_block, statements.StatementBlock)
		self.assertIsInstance(stmt.else_block, statements.StatementBlock)
	
	def test_nested_ifs_single_endif(self):
		stmt = self.analyze("if", '''
			si toto.gentil alors
				bisou(toto)
			sinon si toto.triste alors
				nourrir(toto)
			sinon si toto.age < 5 alors
				au_coin(toto)
			sinon
				fessée(toto)
			fsi''')
		# gentil?
		self.assertIsInstance(stmt.statements.IfThenElse)
		# !gentil, triste?
		self.assertIsInstance(stmt.statements.else_block, statements.IfThenElse)
		# !gentil, !triste, age<5?
		self.assertIsInstance(stmt.statements.else_block.else_block, statements.IfThenElse)
		# !gentil, !triste, !(age<5)
		self.assertIsInstance(stmt.statements.else_block.else_block.else_block, statements.FunctionCall)

	def test_if_missing_keyword(self):
		def test(s):
			self.assertRaises(syntax.ExpectedKeyword, self.analyze, "if", s)
		test("si toto.gentil bisou(toto) fsi")
		test("si toto.gentil alors bisou(toto)")
		test("si toto.gentil alors bisou(toto) sinon fessée(toto)")
	
	def test_if_then_without_condition(self):
		self.assertRaises(syntax.ExpectedItem, self.analyze, "if", "si alors fsi")
	

