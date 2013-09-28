from tests.ldatestcase import LDATestCase
from lda.errors import semantic, handler
from lda.function import Algorithm, Function
from lda import types
from lda.context import ContextStack

class TestLexiconSemantics(LDATestCase):
	def test_variable_absent_from_lexicon(self):
		self.assertLDAError(semantic.MissingDeclaration, self.check, cls=Algorithm,
				program='algorithme lexique début (**)a <- 3 fin')

	def test_composite_in_module_scope(self):
		self.check(program='lexique Moule = <>')

	def test_variable_uses_type_descriptor_with_module_scope(self):
		self.check(program='''\
				lexique
					Moule = <>
				algorithme lexique m : Moule début fin''')

	def test_function_returns_composite(self):
		self.check(program='''\
				lexique
					Moule = <>
				fonction f(): Moule lexique m: Moule début retourne m fin''')

	def test_undefined_type_alias(self):
		alg = self.analyze(cls=Algorithm,
				program='algorithme lexique m: (**)TypeMysterieux début fin')
		alg.check(ContextStack(self.options), handler.DummyHandler())
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

	def test_use_existing_function_name_inside_algorithm_lexicon(self):
		# has to be analyzed as a whole module so that "f" is accounted for
		# in the global lexicon
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, program='''\
				fonction f() lexique début fin
				algorithme
				lexique (**)f: entier
				début fin''')

	def test_use_existing_composite_name_inside_algorithm_lexicon(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, program='''\
				lexique
					M = <>
				fonction f() lexique début fin
				algorithme
				lexique (**)M = <>
				début fin''')

	def test_use_own_function_name_inside_own_lexicon(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, program='''\
				fonction f() lexique (**)f: entier début fin''')

	def test_function_defined_twice(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check, program='''\
				fonction f() lexique début fin
				fonction (**)f() lexique début fin''')

	def test_function_and_global_composite_name_clash(self):
		self.assertLDAError(semantic.DuplicateDeclaration, self.check,
				program='''lexique f = <>
				fonction (**)f() lexique début fin''')

	def test_function_tries_using_function_name_as_return_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, program='''\
				fonction f() lexique début fin
				fonction g(): (**)f lexique début fin''')

	def test_composite_tries_using_function_name_as_member_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, program='''\
				lexique
					Moule = <a: (**)f>
				fonction f() lexique début fin''')

	def test_variable_tries_using_function_name_as_type_alias(self):
		self.assertLDAError(semantic.SemanticError, self.check, program='''\
				fonction wasabi() lexique début fin
				algorithme lexique w: (**)wasabi début fin''')

	def test_inout_non_formal_parameter(self):
		self.assertLDAError(semantic.SemanticError, self.check, program='''\
				algorithme lexique (**)a: inout entier début fin''')

	def test_formal_parameter_absent_from_lexicon(self):
		self.assertLDAError(semantic.FormalParameterMissingInLexicon, self.check,
				cls=Function, program='fonction f((**)a: entier) lexique début fin')

	def test_formal_parameter_absent_from_missing_lexicon(self):
		self.assertLDAError(semantic.FormalParameterMissingInLexicon, self.check,
				cls=Function, program='fonction f((**)a: entier) début fin')

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
		self.check(program='''\
				lexique
					Moule = <>
				fonction f(m: Moule) lexique m: Moule début fin''')

	def test_for_loop_uses_undeclared_counter_variable(self):
		self.assertLDAError(semantic.MissingDeclaration, self.check, program='''\
				algorithme
				lexique
				début
					pour (**)i de 1 jusque 5 faire
					fpour
				fin''')

	def test_variable_of_undeclared_composite_type_used_in_program_body(self):
		self.assertLDAError(semantic.UnresolvableTypeAlias, self.check, program='''\
				algorithme
				lexique
					a: (**)UnMystérieuxCompositeInexistant
				début
					a.b <- 3
				fin''')

	def test_modify_global_variable_in_algorithm(self):
		self.check(program="""\
				lexique globale: entier
				algorithme début globale <- 6 fin""")

	def test_modify_global_variable_in_function(self):
		self.check(program="""\
				lexique globale: entier
				fonction f() début globale <- 6 fin""")

