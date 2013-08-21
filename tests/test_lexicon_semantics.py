from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestLexiconSemantics(LDATestCase):
	def test_array_type_using_variable_in_its_dimensions(self):
		self.check('algorithm', '''\
				algorithme
				lexique t: tableau entier[0..n] n: entier
				début fin''')

	def test_variable_absent_from_lexicon(self):
		self.assertRaises(semantic.MissingDeclaration, self.check, 'algorithm',
			'algorithme lexique début a <- 3 fin')

	def test_composite_in_module_scope(self):
		self.check('module', 'Moule = <>')

	def test_variable_uses_type_descriptor_with_module_scope(self):
		self.check('module', '''\
				Moule = <>
				algorithme lexique m : Moule début fin''')

	def test_function_returns_composite(self):
		self.check('module', '''\
				Moule = <>
				fonction f(): Moule lexique début fin''')

	def test_undefined_type_alias(self):
		self.assertRaises(semantic.MissingDeclaration, self.check, 'algorithm',
			'algorithme lexique m: TypeMysterieux début fin')

	def test_variable_declared_twice(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'algorithm',
			'algorithme lexique a:entier a:entier début fin')

	def test_composite_declared_twice(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'algorithm',
			'algorithme lexique M=<> M=<> début fin')

	def test_composite_and_variable_with_same_name(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'algorithm',
			'algorithme lexique a=<> a:entier début fin')

	def test_use_existing_function_name_for_variable_and_try_calling_it(self):
		# has to be analyzed as a whole module so that "f" is accounted for
		# in the global lexicon
		self.assertRaises(semantic.NonCallable, self.check, 'module', '''\
			fonction f() lexique début fin
			algorithme
			lexique f: entier
			début f() fin''')

	def test_function_defined_twice(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'module', '''\
			fonction f() lexique début fin
			fonction f() lexique début fin''')

	def test_function_and_global_composite_name_clash(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'module', '''\
			fonction f() lexique début fin
			f = <>''')

	def test_cyclic_composite(self):
		self.assertRaises(semantic.SemanticError, self.check, 'module',
				'algorithme lexique Moule = <m: Moule> début fin')

	def test_function_tries_using_function_name_as_return_type_alias(self):
		self.assertRaises(semantic.SemanticError, self.check, 'module', '''\
				fonction f() lexique début fin
				fonction g(): f lexique début fin''')

	def test_composite_tries_using_function_name_as_member_type_alias(self):
		self.assertRaises(semantic.SemanticError, self.check, 'module', '''\
				fonction f() lexique début fin
				Moule = <a: f>''')

	def test_variable_tries_using_function_name_as_type_alias(self):
		self.assertRaises(semantic.SemanticError, self.check, 'module', '''\
				fonction wasabi() lexique début fin
				algorithme lexique w: wasabi début fin''')

