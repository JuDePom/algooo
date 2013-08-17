from tests.parsertestcase import ParserTestCase
from lda import expression, operators, errors

class test_expression_parsing(ParserTestCase):
	def _expr(self, buf):
		return self.analyze('expression', buf)

	def _literal(self, expression_string, cls, convert):
		literal = self._expr(expression_string)
		self.assertIsInstance(literal, cls)
		self.assertEqual(literal.value, convert(expression_string))
			
	def test_literal_integers(self):
		test = lambda s: self._literal(s, expression.LiteralInteger, int)
		test('1')
		test(' 1')
		test('1 ')
		test(' 1 ')
		test('12')
		test('123')
		test('01')
		test('0123456789000000000')

	def test_literal_reals(self):
		test = lambda s: self._literal(s, expression.LiteralReal, float)
		test('1.')
		test('1. ')
		test('1.0')
		test('1.01')
		test('1.012')
		test('123.4567')
		test('.0')
		test('.01')
		test('.023')
		test('.0456')

	def test_incomplete_binary_operations(self):
		test = lambda s: self.assertRaises(errors.LDASyntaxError, self._expr, s)
		test('1-')
		test('1 -')
		test('1+')
		test('1 +')
		test('1*')
		test('1 *')
		test('1/')
		test('1 /')
		test('1 mod ')
		test('1..')
		test('1 ..')
		test('ident [')
		test('ident.')
		test('..')
		test('*')
		test('/')
		test('mod')
		test('.')
		test('moule. .champ')
		test('oh_no [ the_closing_square_bracket_is_missing')
	
	def test_root_in_binary_operation_tree(self):
		test = lambda s, cls: self.assertIsInstance(self._expr(s), cls)
		test('1+1', operators.Addition)
		test('1-1', operators.Subtraction)
		test('1/1', operators.Division)
		test('1*1', operators.Multiplication)
		test('1..2', operators.IntegerRange)
		test('ident[ident]', operators.ArraySubscript)
		test('ident.ident', operators.MemberSelect)
		test('ident()', operators.FunctionCall)
		test('ident(ident)', operators.FunctionCall)
		test('ident(ident, ident, ident)', operators.FunctionCall)
		test('1+1*1', operators.Addition)
		test('1*1+1', operators.Addition)
		test('(1+1)*1', operators.Multiplication)
		test('1*(1+1)', operators.Multiplication)
		test('1+1/1', operators.Addition)
		test('1/1+1', operators.Addition)
		test('ident[ident].ident', operators.MemberSelect)
		test('ident.ident[ident]', operators.ArraySubscript)
		test('ident <- ident < ident', operators.Assignment)
		test('ident(ident < ident)', operators.FunctionCall)

	def test_array_subscript(self):
		def test(s, indices):
			subscript = self._expr(s)
			self.assertIsInstance(subscript, operators.ArraySubscript)
			self.assertIsInstance(subscript.rhs, expression.Varargs)
			self.assertEqual(len(subscript.rhs), len(indices))
			for rhs_int, reference in zip(subscript.rhs, indices):
				self.assertIsInstance(rhs_int, expression.LiteralInteger)
				self.assertEqual(rhs_int.value, reference)
		test('t[0]', [0])
		test('t[0,1]', [0,1])
		test('t[0,1,2]', [0,1,2])
		test('t[   25, 05 ,   1991 ]', [25,5,1991])

