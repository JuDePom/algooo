from tests.ldatestcase import LDATestCase
from lda import expression
from lda import operators
from lda import kw
from lda.statements import For, StatementBlock
from lda.errors import syntax

class TestForSyntax(LDATestCase):
	def test_for_good_syntax(self):
		stmt = self.analyze(cls=For,
				program="pour i de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, expression.ExpressionIdentifier)
		self.assertIsInstance(stmt.initial, expression.LiteralInteger)
		self.assertIsInstance(stmt.final, expression.LiteralInteger)
		self.assertIsInstance(stmt.block, StatementBlock)

	def test_for_with_array_element_counter(self):
		stmt = self.analyze(cls=For,
				program="pour t[0] de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.ArraySubscript)

	def test_for_with_composite_member_counter(self):
		stmt = self.analyze(cls=For,
				program="pour moule.compteur de 1 jusque 3 faire fessée(toto) fpour")
		self.assertIsInstance(stmt.counter, operators.MemberSelect)

	def test_for_missing_keywords(self):
		def test(program, keyword):
			self.assertMissingKeywords(keyword, cls=For, program=program)
		test("pour i(**)1 jusque 3 faire fessée(toto) fpour", kw.FROM)
		test("pour i de 1(**)3 faire fessée(toto) fpour", kw.TO)
		test("pour i de 1 jusque 3(**)fessée(toto) fpour", kw.DO)
		test("pour i de 1 jusque 3 faire fessée(toto)(**)", kw.END_FOR)

	def test_for_wrong_ending_keyword(self):
		self.assertMissingKeywords(kw.END_FOR, cls=For,
				program="pour i de 1 jusque 3 faire fessée(toto) (**)fpou")

	def test_for_alternative_from_keyword(self):
		self.analyze(cls=For,
				program="pour i de 1 à 3 faire fessée(toto) fpour")

