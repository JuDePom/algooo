from tests.ldatestcase import LDATestCase
from lda import expression
from lda.statements import While, StatementBlock
from lda.errors import syntax

class TestWhileSyntax(LDATestCase):
	def test_while_good_syntax(self):
		stmt = self.analyze(While, "tantque toto.gentil faire bisou(toto) ftant")
		self.assertIsInstance(stmt.condition, expression.Expression)
		self.assertIsInstance(stmt.block, StatementBlock)
	
	def test_while_alternative_keywords(self):
		self.analyze(While, "tantque toto.gentil faire bisou(toto) ftantque")
	
	def test_while_missing_keyword(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedKeyword, self.analyze, cls=While, program=p)
		test("tantque toto.gentil (**)bisou(toto) ftant")
		test("tantque toto.gentil faire bisou(toto)(**)")
		test("tantque toto.gentil(**)")
	
	def test_while_missing_condition(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=While, program=p)
		test("tantque(**)faire bisou(toto) ftant")
		test("tantque(**)")
	
