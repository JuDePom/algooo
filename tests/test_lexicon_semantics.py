from tests.ldatestcase import LDATestCase
from lda.errors import semantic, handler
from lda.module import Module, Algorithm
from lda import types

class TestLexiconSemantics(LDATestCase):
	def test_variable_absent_from_lexicon(self):
		self.assertLDAError(semantic.MissingDeclaration, self.check, cls=Algorithm,
				program='algorithme lexique début (**)a <- 3 fin')

	def test_composite_in_module_scope(self):
		self.check(cls=Module, program='lexique Moule = <>')

	def test_variable_uses_type_descriptor_with_module_scope(self):
		self.check(cls=Module, program='''\
				lexique
					Moule = <>
				algorithme lexique m : Moule début fin''')

	def test_function_returns_composite(self):
		self.check(cls=Module, program='''\
				lexique
					Moule = <>
				fonction f(): Moule lexique début fin''')

	def test_undefined_type_alias(self):
		alg = self.analyze(Algorithm,
				program='algorithme lexique m: (**)TypeMysterieux début fin')
		alg.check({}, handler.DummyHandler())
		self.assertIs(types.ERRONEOUS, alg.lexicon.symbol_dict['m'].resolved_type)

	def test_variable_declared_twice(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Algorithm,
				program='algorithme lexique a:entier (**)a:entier début fin')

	def test_variable_uses_its_own_name_as_type(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Algorithm,
				program='algorithme lexique a:(**)a début fin')

	def test_composite_declared_twice(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Algorithm,
				program='algorithme lexique M=<> (**)M=<> début fin')

	def test_composite_and_variable_with_same_name(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Algorithm,
				program='algorithme lexique a=<> (**)a:entier début fin')

	def test_use_existing_function_name_for_variable_and_try_calling_it(self):
		# has to be analyzed as a whole module so that "f" is accounted for
		# in the global lexicon
		self.assertLDAError(semantic.NonCallable, self.check, cls=Module, program='''\
				fonction f() lexique début fin
				algorithme
				lexique f: entier
				début f(**)() fin''')

	def test_function_defined_twice(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Module, program='''\
				fonction f() lexique début fin
				fonction (**)f() lexique début fin''')

	def test_function_and_global_composite_name_clash(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, cls=Module,
				program='''lexique f = <>
				fonction (**)f() lexique début fin''')

	def test_function_tries_using_function_name_as_return_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module, program='''\
				fonction f() lexique début fin
				fonction g(): (**)f lexique début fin''')

	def test_composite_tries_using_function_name_as_member_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module, program='''\
				lexique
					Moule = <a: (**)f>
				fonction f() lexique début fin''')

	def test_variable_tries_using_function_name_as_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, cls=Module, program='''\
				fonction wasabi() lexique début fin
				algorithme lexique w: (**)wasabi début fin''')

