from tests.ldatestcase import LDATestCase

class TestBuiltinFunctionCallSyntax(LDATestCase):
	def test_println_call(self):
		self.analyze("algorithme début écrire(\"bonjour\") fin")

