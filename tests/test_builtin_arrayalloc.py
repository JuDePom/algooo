from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestBuiltinArrayAlloc(LDATestCase):
	def test_arrayalloc_call_on_static_array(self):
		self.assertLDAError(semantic.TypeError, analyzer=self.check, program="""\
				algorithme
				lexique
					t: tableau entier[0..5]
				début
					tailletab((**)t, 0..5)
				fin""")

