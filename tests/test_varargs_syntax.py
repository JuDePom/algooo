from tests.ldatestcase import LDATestCase
from lda import typedesc
from lda import expression
from lda.errors import syntax

class TestVarargsSyntax(LDATestCase):
	def _analyze_id_varargs(self, buf):
		varargs = self.analyze('varargs', buf, self.parser.analyze_identifier)
		self.assertIsInstance(varargs, expression.Varargs)
		return varargs

	def test_varargs_0(self):
		varargs = self._analyze_id_varargs("")
		self.assertEquals(len(varargs), 0)

	def test_varargs_1(self):
		varargs = self._analyze_id_varargs("ident")
		self.assertEquals(len(varargs), 1)
		for arg in varargs:
			self.assertIsInstance(arg, typedesc.Identifier)
	
	def test_varargs_2(self):
		varargs = self._analyze_id_varargs("ident, ident")
		self.assertEquals(len(varargs), 2)
		for arg in varargs:
			self.assertIsInstance(arg, typedesc.Identifier)

	def test_varargs_with_empty_arg(self):
		self.assertRaises(syntax.SyntaxError,
				self._analyze_id_varargs, "ident,,ident")
