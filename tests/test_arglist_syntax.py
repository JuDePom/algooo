from tests.ldatestcase import LDATestCase
from lda import expression
from lda.errors import syntax

class TestArglistSyntax(LDATestCase):
	def _id_arglist(self, program):
		return self.analyze(program, list,
				analyze_arg=self.parser.analyze_expression_identifier)

	def test_0_args(self):
		arglist = self._id_arglist("")
		self.assertEqual(len(arglist), 0)

	def test_1_arg(self):
		arglist = self._id_arglist("ident")
		self.assertEqual(len(arglist), 1)
		for arg in arglist:
			self.assertIsInstance(arg, expression.ExpressionIdentifier)

	def test_2_args(self):
		arglist = self._id_arglist("ident, ident")
		self.assertEqual(len(arglist), 2)
		for arg in arglist:
			self.assertIsInstance(arg, expression.ExpressionIdentifier)

	def test_arglist_with_empty_arg(self):
		self.assertLDAError(syntax.SyntaxError, self.analyze,
				program='ident,(**),ident',
				cls=list,
				analyze_arg=self.parser.analyze_expression_identifier)

