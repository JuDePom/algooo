from .ldatestcase import LDATestCase
from lda.errors import semantic

class TestFriendlySemanticErrors(LDATestCase):
	def test_only_1_error_about_erroneous_array_referenced_later(self):
		self.assertMultipleSemanticErrors([semantic.TypeError], """\
				algorithme
				lexique
					t: tableau entier[(**)"xxx"]
					u: tableau entier[0..3]
				début
					t <- u
				fin""")

	def test_3_errors_about_array_with_3_erroneous_dimensions(self):
		self.assertMultipleSemanticErrors(
				[semantic.TypeError, semantic.TypeError, semantic.TypeError],
				"""algorithme
				lexique
					t: tableau entier[(**)"xxx", (**)'a', (**)5.123]
				début fin""")

