from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestBuiltinPrint(LDATestCase):
	def test_print_call_with_string(self):
		self.check(program="algorithme début écrire(\"bonjour\") fin")

	def test_print_call_with_nothing(self):
		self.check(program="algorithme début écrire() fin")

	def test_print_call_with_void_argument(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
			fonction f() début retourne fin
			algorithme début écrire((**)f()) fin""")

	def test_print_call_with_not_a_variable_argument(self):
		self.assertLDAError(semantic.TypeError, self.check, program="""\
			fonction f() début retourne fin
			algorithme début écrire((**)f) fin""")

