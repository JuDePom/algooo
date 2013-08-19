from tests.ldatestcase import LDATestCase
from lda import expression
from lda import operators
from lda import statements
from lda import typedesc
from lda.errors import syntax

class TestForSyntax(LDATestCase):
	def test_for_good_syntax(self):
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

	def test_for_missing_keywords(self):
		def test(p):
			self.assert_syntax_error(syntax.ExpectedKeyword, analyze='for', program=p)
		test("pour i(**)1 jusque 3 faire fessée(toto) fpour")
		test("pour i de 1(**)3 faire fessée(toto) fpour")
		test("pour i de 1 jusque 3(**)fessée(toto) fpour")
		test("pour i de 1 jusque 3 faire fessée(toto)(**)")
	
