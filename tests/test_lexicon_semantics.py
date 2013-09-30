from tests.ldatestcase import LDATestCase
from lda.errors import semantic, handler
from lda import types
from lda.context import ContextStack

class TestLexiconSemantics(LDATestCase):

	def test_undefined_type_alias(self):
		module = self.analyze(program="""\
				algorithme
				lexique
					a: entier
					m: (**)TypeMysterieux
				début
				fin""")
		module.check(ContextStack(self.options), handler.DummyHandler())
		self.assertIs(types.ERRONEOUS, module.algorithms[0].lexicon['m'].resolved_type)

