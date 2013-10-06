from tests.ldatestcase import LDATestCase

class TestJSExpressions(LDATestCase):
	def _test(self, lda_expression_string, expected_result_string):
		result = self.jseval(
				program="algorithme début écrire({}) fin".format(lda_expression_string))
		self.assertEqual(result, expected_result_string)

	def test_literal_arithmetic(self):
		self._test("1+1", "2")
		self._test("1-1", "0")
		self._test("3./2", "1.5")
		self._test("2**9", "512")
		self._test("6 mod 4", "2")

	def test_unary_number_operators(self):
		self._test("-123", "-123")
		self._test("-123.456", "-123.456")
		self._test("+123", "123")
		self._test("+123.456", "123.456")
		self._test("-(1+1)", "-2")

	def test_function_call_return_nothing(self):
		self.jseval(program="""\
				fonction f() début retourne fin
				algorithme début f() fin""")

	def test_unary_not(self):
		self._test("non vrai", "false")
		self._test("non faux", "true")

	def test_logical_ops(self):
		self._test("vrai et vrai", "true")
		self._test("vrai et faux", "false")
		self._test("faux et vrai", "false")
		self._test("faux et faux", "false")
		self._test("vrai ou vrai", "true")
		self._test("vrai ou faux", "true")
		self._test("faux ou vrai", "true")
		self._test("non faux ou faux", "true")
		self._test("faux ou non faux", "true")
		self._test("non faux et non faux", "true")

