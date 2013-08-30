from tests.ldatestcase import LDATestCase
from lda.symbols import Identifier
from lda.errors import syntax

class TestArglistSyntax(LDATestCase):
	def _id_arglist(self, program):
		return self.analyze(list, program,
				analyze_arg=self.parser.analyze_identifier)

	def test_0_args(self):
		arglist = self._id_arglist("")
		self.assertEqual(len(arglist), 0)

	def test_1_arg(self):
		arglist = self._id_arglist("ident")
		self.assertEqual(len(arglist), 1)
		for arg in arglist:
			self.assertIsInstance(arg, Identifier)

	def test_2_args(self):
		arglist = self._id_arglist("ident, ident")
		self.assertEqual(len(arglist), 2)
		for arg in arglist:
			self.assertIsInstance(arg, Identifier)

	def test_arglist_with_empty_arg(self):
		self.assertLDAError(syntax.SyntaxError, self.analyze,
				cls=list,
				program='ident,(**),ident',
				analyze_arg=self.parser.analyze_identifier)

