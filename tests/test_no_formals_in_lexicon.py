from tests.ldatestcase import LDATestCase
from lda.errors import semantic, handler
from lda.context import ContextStack

class TestNoFormalsInLexicon(LDATestCase):
	def setUp(self):
		super().setUp()
		self.options.formals_in_lexicon = False

	def test_one_warning_if_formal_parameter_redefined_in_lexicon(self):
		self.assertMultipleSemanticErrors([semantic.SemanticError],
				program="""\
				(*% formals_in_lexicon False %*)
				fonction f(a: entier)
				lexique
					(**)a: entier
					b: entier
				début
					a <- 3
					b <- 3
				fin""")

