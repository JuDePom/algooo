from tests.ldatestcase import LDATestCase
from lda import expression
from lda import operators
from lda.statements import For, StatementBlock
from lda.symbols import Identifier
from lda.errors import syntax

class TestForSyntax(LDATestCase):
	def test_for_good_syntax(self):
		stmt = self.analyze(For, "pour i de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, Identifier)
		self.assertIsInstance(stmt.initial, expression.LiteralInteger)
		self.assertIsInstance(stmt.final, expression.LiteralInteger)
		self.assertIsInstance(stmt.block, StatementBlock)

	def test_for_with_array_element_counter(self):
		stmt = self.analyze(For, "pour t[0] de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.ArraySubscript)

	def test_for_with_composite_member_counter(self):
		stmt = self.analyze(For, "pour moule.compteur de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.MemberSelect)

	def test_for_missing_keywords(self):
		def test(p):
			self.assertLDAError(syntax.ExpectedKeyword, self.analyze, cls=For, program=p)
		test("pour i(**)1 jusque 3 faire fessée(toto) fpour")
		test("pour i de 1(**)3 faire fessée(toto) fpour")
		test("pour i de 1 jusque 3(**)fessée(toto) fpour")
		test("pour i de 1 jusque 3 faire fessée(toto)(**)")
	
