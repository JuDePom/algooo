from tests.ldatestcase import LDATestCase
from lda.errors import semantic
from lda.module import Function, Module

class TestFormalParameterSemantics(LDATestCase):
	def test_formal_parameter_absent_from_lexicon(self):
		self.assertLDAError(semantic.FormalParameterMissingInLexicon, self.check,
				cls=Function, program='fonction f((**)a: entier) lexique début fin')

	def test_scalar_formal_parameter_present_in_lexicon(self):
		self.check(cls=Function,
				program='fonction f(a: entier) lexique a: entier début fin')

	def test_static_array_formal_parameter_present_in_lexicon(self):
		self.check(cls=Function, program='''fonction f(a: tableau entier[0..5])
				lexique a: tableau entier[0..5] début fin''')

	def test_formal_parameter_different_type_in_lexicon(self):
		self.assertLDAError(semantic.TypeMismatch, self.check, cls=Function,
				program='fonction f(a: entier) lexique (**)a: réel début fin')

	def test_duplicate_formal_parameter_inside_parentheses(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Function,
				program='fonction f(a: entier, (**)a:entier) lexique a: entier début fin')

	def test_formal_parameter_uses_external_type_descriptor(self):
		self.check(cls=Module, program='''\
				lexique
					Moule = <>
				fonction f(m: Moule) lexique m: Moule début fin''')

