from tests.ldatestcase import LDATestCase
from lda import expression
from lda import kw
from lda.statements import While, StatementBlock
from lda.errors import syntax

class TestWhileSyntax(LDATestCase):
	def test_while_good_syntax(self):
		stmt = self.analyze(cls=While,
				program="tantque toto.gentil faire bisou(toto) ftant")
		self.assertIsInstance(stmt.condition, expression.Expression)
		self.assertIsInstance(stmt.body, list)
	
	def test_while_alternative_keywords(self):
		self.analyze(cls=While,
				program="tantque toto.gentil faire bisou(toto) ftantque")
	
	def test_while_missing_keyword(self):
		def test(program, *keywords):
			self.assertMissingKeywords(*keywords, cls=While, program=program)
		test("tantque toto.gentil (**)bisou(toto) ftant", kw.DO)
		test("tantque toto.gentil faire bisou(toto)(**)", kw.END_WHILE)
		test("tantque toto.gentil(**)", kw.DO)
	
	def test_while_missing_condition(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedItem, self.analyze, cls=While, program=p)
		test("tantque(**)faire bisou(toto) ftant")
		test("tantque(**)")
	
