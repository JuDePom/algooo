from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.types import Composite
from lda.module import Module

class TestCompositeTypeSemantics(LDATestCase):
	def test_duplicate_fields_in_composite(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Composite,
				program='Moule = <a:entier, (**)a:chaîne>')

	def test_composite_complex_cross_references(self):
		self.check(cls=Module, program='''\
				algorithme
				lexique
					Niveau3 = <a: Niveau2>
					Niveau1 = <a: entier>
					Niveau2 = <a: tableau Niveau1[0..2, 0..3]>
					n3 : Niveau3
				début fin''')

	def test_recursive_composite(self):
		self.assertLDAError(semantic.RecursiveDeclaration, self.check, cls=Module,
				program='algorithme lexique Moule = <(**)m:Moule> début fin')

	def test_recursive_composite_cross_references(self):
		self.assertLDAError(semantic.RecursiveDeclaration, self.check, cls=Module, program='''\
				algorithme
				lexique
					MouleRecursive1 = <m: MouleRecursive2>
					MouleRecursive2 = <(**)m: MouleRecursive1>
				début fin''')

