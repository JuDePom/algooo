from tests.ldatestcase import LDATestCase
from lda import expression
from lda import statements
from lda.errors import syntax

class TestWhileSyntax(LDATestCase):
	def test_while_good_syntax(self):
		stmt = self.analyze("while", "tantque toto.gentil faire bisou(toto) ftant")
		self.assertIsInstance(stmt, statements.While)
		self.assertIsInstance(stmt.condition, expression.Expression)
		self.assertIsInstance(stmt.block, statements.StatementBlock)
	
	def test_while_alternative_keywords(self):
		stmt = self.analyze("while", "tantque toto.gentil faire bisou(toto) ftantque")
		self.assertIsInstance(stmt, statements.While)
	
	def test_while_missing_keyword(self):
		def test(s):
			self.assertRaises(syntax.ExpectedKeyword, self.analyze, "while", s)
		test("tantque toto.gentil bisou(toto) ftant")
		test("tantque toto.gentil faire bisou(toto)")
		test("tantque toto.gentil")
	
	def test_while_missing_condition(self):
		self.assertRaises(syntax.ExpectedItem, self.analyze, "while",
				"tantque (* pas de condition! *) faire bisou(toto) ftant")
		self.assertRaises(syntax.ExpectedItem, self.analyze, "while",
				"tantque")
	
