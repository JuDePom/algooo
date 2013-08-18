from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class test_lexicon_semantics(LDATestCase):
	def test_formal_parameter_absent_from_lexicon(self):
		self.assertRaises(semantic.SemanticError, self.check, 'function',
			'fonction f(a: entier) lexique début fin')

	def test_formal_parameter_present_in_lexicon(self):
		self.check('function', 'fonction f(a: entier) lexique début fin')

	def test_variable_absent_from_lexicon(self):
		self.assertRaises(semantic.MissingDeclaration, self.check, 'algorithm',
			'algorithme lexique début a <- 3 fin')

	def test_undefined_type_alias(self):
		self.assertRaises(semantic.MissingDeclaration, self.check, 'algorithm',
			'algorithme lexique m: TypeMysterieux début fin')

	def test_variable_declared_twice(self):
		self.assertRaises(semantic.DuplicateDeclaration, self.check, 'algorithm',
			'algorithme lexique a:entier b:entier début fin')
	
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

