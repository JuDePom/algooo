from tests.ldatestcase import LDATestCase
from lda.errors import handler
from lda import types
from lda.context import ContextStack

class TestLexiconSemantics(LDATestCase):
	def test_undefined_type_alias(self):
		module = self.analyze(program="""\
				algorithme
				lexique
					m: (**)TypeMysterieux
				début
				fin""")
		module.check(ContextStack(self.options), handler.DummyHandler())
		m = module.algorithms[0].lexicon.variables[0]
		self.assertEqual("m", m.ident.name)
		self.assertIs(types.ERRONEOUS, m.resolved_type)

