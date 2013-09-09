from tests.ldatestcase import LDATestCase
from lda import expression
from lda import operators
from lda.symbols import Identifier
from lda.errors import syntax

class TestExpressionSyntax(LDATestCase):
	def _literal(self, cls, expression_string, convert):
		literal = self.analyze(expression_string, cls)
		self.assertEqual(literal.value, convert(expression_string))
			
	def test_literal_integers(self):
		test = lambda s: self._literal(expression.LiteralInteger, s, int)
		test("1")
		test(" 1")
		test("1 ")
		test(" 1 ")
		test("12")
		test("123")
		test("01")
		test("0123456789000000000")

	def test_literal_reals(self):
		test = lambda s: self._literal(expression.LiteralReal, s, float)
		test("1.")
		test("1. ")
		test("1.0")
		test("1.01")
		test("1.012")
		test("123.4567")
		test(".0")
		test(".01")
		test(".023")
		test(".0456")

	def test_integer_literals_within_range(self):
		rangeop = self.analyze("0..1", operators.IntegerRange)
		self.assertIsInstance(rangeop.lhs, expression.LiteralInteger)
		self.assertIsInstance(rangeop.rhs, expression.LiteralInteger)
		self.assertEqual(rangeop.lhs.value, 0)
		self.assertEqual(rangeop.rhs.value, 1)

	def test_real_literals_within_range(self):
		rangeop = self.analyze("0.123..4.567", operators.IntegerRange)
		# Yes, it's an integer range with reals in it, but type checking is part
		# of the semantic analysis. We're just checking the syntax for now.
		self.assertIsInstance(rangeop.lhs, expression.LiteralReal)
		self.assertIsInstance(rangeop.rhs, expression.LiteralReal)
		self.assertEqual(rangeop.lhs.value, 0.123)
		self.assertEqual(rangeop.rhs.value, 4.567)
	
	def test_identifiers_within_range(self):
		rangeop = self.analyze("a..b", operators.IntegerRange)
		self.assertIsInstance(rangeop.lhs, Identifier)
		self.assertIsInstance(rangeop.rhs, Identifier)
		self.assertEqual(rangeop.lhs.name, "a")
		self.assertEqual(rangeop.rhs.name, "b")

	def test_incomplete_binary_operations(self):
		def test(s):
			self.assertLDAError(syntax.ExpectedItem, self.analyze,
					program=s, cls=expression.Expression)
		test("1-(**)")
		test("1 -(**)")
		test("1+(**)")
		test("1 +(**)")
		test("1*(**)")
		test("1 *(**)")
		test("1/(**)")
		test("1 /(**)")
		test("1 mod (**)")
		test("1..(**)")
		test("1 ..(**)")
		test("ident [(**)")
		test("ident.(**)")
		test("(**)..")
		test("(**)*")
		test("(**)/")
		test("(**)mod")
		test("(**).")
		test("moule. (**).champ")
		test("oh_no [ the_closing_square_bracket_is_missing(**)")
	
	def test_root_in_binary_operation_tree(self):
		self.analyze("1+1", operators.Addition)
		self.analyze("1-1", operators.Subtraction)
		self.analyze("1/1", operators.Division)
		self.analyze("1*1", operators.Multiplication)
		self.analyze("1..2", operators.IntegerRange)
		self.analyze("ident[ident]", operators.ArraySubscript)
		self.analyze("ident.ident", operators.MemberSelect)
		self.analyze("ident()", operators.FunctionCall)
		self.analyze("ident(ident)", operators.FunctionCall)
		self.analyze("ident(ident, ident, ident)", operators.FunctionCall)
		self.analyze("1+1*1", operators.Addition)
		self.analyze("1*1+1", operators.Addition)
		self.analyze("(1+1)*1", operators.Multiplication)
		self.analyze("1*(1+1)", operators.Multiplication)
		self.analyze("1+1/1", operators.Addition)
		self.analyze("1/1+1", operators.Addition)
		self.analyze("1+1=2", operators.Equal)
		self.analyze("2=1+1", operators.Equal)
		self.analyze("ident[ident].ident", operators.MemberSelect)
		self.analyze("ident.ident[ident]", operators.ArraySubscript)
		self.analyze("ident(ident < ident)", operators.FunctionCall)

	def test_array_subscript(self):
		def test(s, indices):
			subscript = self.analyze(s, operators.ArraySubscript)
			self.assertIsInstance(subscript.rhs, list)
			self.assertEqual(len(subscript.rhs), len(indices))
			for rhs_int, reference in zip(subscript.rhs, indices):
				self.assertIsInstance(rhs_int, expression.LiteralInteger)
				self.assertEqual(rhs_int.value, reference)
		test("t[0]", [0])
		test("t[0,1]", [0,1])
		test("t[0,1,2]", [0,1,2])
		test("t[   25, 05 ,   1991 ]", [25,5,1991])

