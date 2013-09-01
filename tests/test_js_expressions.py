from tests.ldatestcase import LDATestCase

class TestJSExpressions(LDATestCase):
	def _test(self, lda_expression_string, expected_result_string):
		result = self.jseval(
				program="algorithme début écrire({}) fin".format(lda_expression_string))
		self.assertEqual(result, expected_result_string)

	def test_literal_arithmetic(self):
		self._test("1+1", "2\n")
		self._test("1-1", "0\n")
		self._test("3./2", "1.5\n")
		self._test("2**9", "512\n")
		self._test("6 mod 4", "2\n")
	
	def test_function_call_return_value(self):
		self.assertEqual("1234\n", self.jseval(program="""\
				fonction f() début retourne 1234 fin
				algorithme début écrire(f()) fin"""))

