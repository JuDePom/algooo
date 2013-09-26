from tests.ldatestcase import LDATestCase
from lda.errors import syntax
from lda.function import Algorithm, Function
from lda.types import Array

class TestArraySyntax(LDATestCase):
	def test_incomplete_intrange(self):
		self.assertLDAError(syntax.MissingRightOperand, self.analyze, cls=Array,
				program='tableau entier[1 (**)..]')

	def test_illegal_nested_array_syntax(self):
		# This one has to be parsed as an entire algorithm, not just as a bare
		# lexicon. This is because a lexicon is delimited by the first unknown
		# token encountered by the parser. By parsing an entire algorithm, the
		# unknown token will be passed back to the algorithm, which won't know
		# what to do with it, and will raise a syntax error.
		self.assertLDAError(syntax.SyntaxError, self.analyze, cls=Algorithm,
				program="""\
				algorithme
				lexique
					a: tableau(**)tableau entier [0..5][0..5]
				début fin""")

