from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.types import Composite
from lda.vardecl import VarDecl

class TestArglistSyntax(LDATestCase):
	"""
	This class tests arglists through a Composite's fields attribute, i.e. a
	list of VarDecls.
	"""

	def _arglist(self, program):
		return self.analyze(program, Composite, ident=None).fields

	def test_0_arg(self):
		arglist = self._arglist("<>")
		self.assertEqual(len(arglist), 0)

	def test_1_arg(self):
		arglist = self._arglist("<a:entier>")
		self.assertEqual(len(arglist), 1)
		for arg in arglist:
			self.assertIsInstance(arg, VarDecl)

	def test_2_args(self):
		arglist = self._arglist("<a:entier, b:entier>")
		self.assertEqual(len(arglist), 2)
		for arg in arglist:
			self.assertIsInstance(arg, VarDecl)

	def test_arglist_with_empty_arg(self):
		self.assertLDAError(syntax.SyntaxError, self._arglist,
				program="<(**),,,>")

