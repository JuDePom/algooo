from . import ldatestcase
from lda import expression, typedesc, position
from lda import operators as ops

class TestExpressionEqualities(ldatestcase.LDATestCase):
	def test_literal_integer_equality(self):
		a = expression.LiteralInteger(None, 4)
		b = expression.LiteralInteger(None, 4)
		c = expression.LiteralInteger(None, 6)
		d = expression.LiteralInteger(None, 6)
		self.assertEqual(a, b)
		self.assertEqual(c, d)
		self.assertNotEqual(a, c)
		self.assertNotEqual(a, d)
		self.assertNotEqual(b, c)
		self.assertNotEqual(b, d)

	def test_literal_integer_not_equal_to_other_literal_types(self):
		a = expression.LiteralInteger(None, 4)
		b = expression.LiteralReal(None, 4)
		c = expression.LiteralBoolean(None, True)
		d = expression.LiteralString(None, "4")
		e = expression.LiteralCharacter(None, '4')
		self.assertNotEqual(a, b)
		self.assertNotEqual(a, c)
		self.assertNotEqual(a, d)
		self.assertNotEqual(a, e)
	
	def test_unary_plus_minus_equalities(self):
		litint1234 = [
				expression.LiteralInteger(None, 1234),
				expression.LiteralInteger(None, 1234),
		]
		litint5678 = expression.LiteralInteger(None, 5678)

		plus1234 = [
				ops.UnaryPlus(None, litint1234[0]),
				ops.UnaryPlus(None, litint1234[0]),
				ops.UnaryPlus(None, litint1234[1]),
		]
		plus5678 = ops.UnaryPlus(None, litint5678)
		minus1234 = ops.UnaryMinus(None, litint1234[0])

		self.assertEqual(plus1234[0], plus1234[0])
		self.assertEqual(plus1234[0], plus1234[1])
		self.assertEqual(plus1234[0], plus1234[2])
		self.assertNotEqual(plus1234[0], plus5678)
		self.assertNotEqual(plus1234[0], minus1234)
	
	def test_identifier_equalities(self):
		identa1 = typedesc.Identifier(position.Position('toto', 2, 3, 4), "a")
		identa2 = typedesc.Identifier(position.Position('toto', 5, 6, 7), "a")
		identb = typedesc.Identifier(position.Position('toto', 2, 3, 4), "b")
		self.assertEqual(identa1, identa1)
		self.assertEqual(identa1, identa2)
		self.assertNotEqual(identa1, identb)
	
	def test_logical_not_equalities(self):
		identa1 = typedesc.Identifier(position.Position('toto', 2, 3, 4), "a")
		identa2 = typedesc.Identifier(position.Position('toto', 5, 6, 7), "a")
		identb = typedesc.Identifier(position.Position('toto', 2, 3, 4), "b")
		not1 = ops.LogicalNot(None, identa1)
		not2 = ops.LogicalNot(None, identa2)
		not3 = ops.LogicalNot(None, identb)
		self.assertEqual(not1, not1)
		self.assertEqual(not1, not2)
		self.assertNotEqual(not1, not3)
		
	def test_range_equalities(self):
		r = lambda program: self.analyze_expression(ops.IntegerRange, program)
		self.assertEqual(r('0..5'), r('  0..5'))
		self.assertEqual(r('0..5'), r('  0 .. 5 '))
		self.assertEqual(r('0..5'), r('0 ..5'))
		self.assertEqual(r('a..b'), r('a..b'))
		self.assertEqual(r('a..a'), r('a..a'))
		self.assertEqual(r('a[5]..a[7]'), r('a[5]..a[7]'))
		self.assertNotEqual(r('0..5'), r('1..5'))
		self.assertNotEqual(r('0..5'), r('0..6'))
		self.assertNotEqual(r('0..5'), r('0..5.00'))
		self.assertNotEqual(r('a..b'), r('c..d'))
		self.assertNotEqual(r('a[5]..a[7]'), r('a[5]..a[6]'))
	
