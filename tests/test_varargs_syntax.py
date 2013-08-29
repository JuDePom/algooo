from tests.ldatestcase import LDATestCase
from lda.symbols import Identifier
from lda import expression
from lda.errors import syntax

class TestVarargsSyntax(LDATestCase):
	def _id_varargs(self, program):
		return self.analyze(expression.Varargs, program,
				analyze_arg=self.parser.analyze_identifier)

	def test_varargs_0(self):
		varargs = self._id_varargs("")
		self.assertEqual(len(varargs), 0)

	def test_varargs_1(self):
		varargs = self._id_varargs("ident")
		self.assertEqual(len(varargs), 1)
		for arg in varargs:
			self.assertIsInstance(arg, Identifier)
	
	def test_varargs_2(self):
		varargs = self._id_varargs("ident, ident")
		self.assertEqual(len(varargs), 2)
		for arg in varargs:
			self.assertIsInstance(arg, Identifier)

	def test_varargs_with_empty_arg(self):
		self.assertLDAError(syntax.SyntaxError, self.analyze,
				cls=expression.Varargs,
				program='ident,(**),ident',
				analyze_arg=self.parser.analyze_identifier)

