import parsertestcase
from lda import expression, operators, errors, statements, typedesc

class test_control_flow_parsing(parsertestcase.ParserTestCase):
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
	
	def test_if_missing_keyword(self):
		def test(s):
			self.assertRaises(errors.ExpectedKeywordError, self.analyze, "if", s)
		test("si toto.gentil bisou(toto) fsi")
		test("si toto.gentil alors bisou(toto)")
		test("si toto.gentil alors bisou(toto) sinon fessée(toto)")
	
	def test_if_then_without_condition(self):
		self.assertRaises(errors.ExpectedItemError, self.analyze, "if", "si alors fsi")
	
	def test_for(self):
		stmt = self.analyze("for", 
				"pour i de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt, statements.For)
		self.assertIsInstance(stmt.counter, typedesc.Identifier)
		self.assertIsInstance(stmt.initial, expression.LiteralInteger)
		self.assertIsInstance(stmt.final, expression.LiteralInteger)
		self.assertIsInstance(stmt.block, statements.StatementBlock)
	
	def test_for_with_complex_counters(self):
		stmt = self.analyze("for", 
				"pour t[0] de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.ArraySubscript)
		stmt = self.analyze("for",
				"pour moule.compteur de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.MemberSelect)

	def test_for_missing_keyword(self):
		def test(s):
			self.assertRaises(errors.ExpectedKeywordError, self.analyze, "for", s)
		test("pour i 1 jusque 3 faire fessée(toto) fpour")
		test("pour i de 1 3 faire fessée(toto) fpour")
		test("pour i de 1 jusque 3 fessée(toto) fpour")
		test("pour i de 1 jusque 3 faire fessée(toto)")
	
	def test_while(self):
		stmt = self.analyze("while", "tantque toto.gentil faire bisou(toto) ftant")
		self.assertIsInstance(stmt, statements.While)
		self.assertIsInstance(stmt.condition, expression.Expression)
		self.assertIsInstance(stmt.block, statements.StatementBlock)
	
	def test_while_alternative_keywords(self):
		stmt = self.analyze("while", "tantque toto.gentil faire bisou(toto) ftantque")
		self.assertIsInstance(stmt, statements.While)
	
	def test_while_missing_keyword(self):
		def test(s):
			self.assertRaises(errors.ExpectedKeywordError, self.analyze, "while", s)
		test("tantque toto.gentil bisou(toto) ftant")
		test("tantque toto.gentil faire bisou(toto)")
		test("tantque toto.gentil")
	
	def test_while_missing_condition(self):
		self.assertRaises(errors.ExpectedItemError, self.analyze, "while",
				"tantque (* pas de condition! *) faire bisou(toto) ftant")
		self.assertRaises(errors.ExpectedItemError, self.analyze, "while",
				"tantque")

	def test_do_while(self):
		stmt = self.analyze("do_while", "faire toto.bisou(toto) tantque toto.gentil")
		self.assertIsInstance(stmt, statements.DoWhile)
		self.assertIsInstance(stmt.block, statements.StatementBlock)
		self.assertIsInstance(stmt.condition, expression.Expression)

