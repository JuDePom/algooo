import unittest
from lda import module, expression, statements, typedesc, operators
import lda.keywords as kw

def _id(name):
	return typedesc.Identifier(None, name)

def _bogus_block(name_a, name_b):
	'''
	Return a StatementBlock containing an assignment of name_b to name_a
	'''
	assignment = operators.Assignment(None, _id(name_a), _id(name_b))
	return statements.StatementBlock(None, [assignment])

class test_lda_output(unittest.TestCase):
	def test_scalar_types(self):
		self.assertEqual(typedesc.Integer.lda_format(), kw.INT.default_spelling)
		self.assertEqual(typedesc.Real.lda_format(), kw.REAL.default_spelling)
		self.assertEqual(typedesc.String.lda_format(), kw.STRING.default_spelling)
		self.assertEqual(typedesc.Boolean.lda_format(), kw.BOOL.default_spelling)

	def test_lexicon(self):
		expected = (
				"{0.LEXICON}\n"
				"\tMoule = <prix : {0.INT}, nom : {0.STRING}>\n"
				"\ttab : tableau Moule[0 .. i, 0 .. j]").format(kw)
		moule = typedesc.CompositeType(_id("Moule"), [
				typedesc.Field(_id("prix"), typedesc.Integer),
				typedesc.Field(_id("nom"), typedesc.String)])
		moule_alias = typedesc.TypeAlias(None, "Moule")
		range_i = operators.IntegerRange(None, expression.LiteralInteger(None, 0), _id("i"))
		range_j = operators.IntegerRange(None, expression.LiteralInteger(None, 0), _id("j"))
		tab = typedesc.Array(moule_alias, [range_i, range_j])
		tab_field = typedesc.Field(_id("tab"), tab)
		lexicon = typedesc.Lexicon(variables=[tab_field], composites=[moule])
		self.assertEqual(lexicon.lda_format(), expected)

	def test_literals(self):
		self.assertEqual(expression.LiteralInteger(None, 1).lda_format(), "1")
		self.assertEqual(expression.LiteralReal(None, 1.1).lda_format(), "1.1")
		self.assertEqual(expression.LiteralReal(None, .1).lda_format(), "0.1")
		self.assertEqual(expression.LiteralString(None, "I am a string").lda_format(), "\"I am a string\"")
		self.assertEqual(expression.LiteralBoolean(None, True).lda_format(), kw.TRUE.default_spelling)
		self.assertEqual(expression.LiteralBoolean(None, False).lda_format(), kw.FALSE.default_spelling)	
	
	def test_varargs(self):
		expected = "a : {0.INT}, b : {0.STRING}".format(kw)
		field1 = typedesc.Field(_id("a"),typedesc.Integer)
		field2 = typedesc.Field(_id("b"),typedesc.String)
		varargs = expression.Varargs(None, [field1, field2])
		self.assertEqual(varargs.lda_format(), expected)

	def test_if_then(self):
		expected_if_then = (
				"{0.IF} a {0.LE} b {0.THEN}\n"
				"\ta {0.ASSIGN} b\n"
				"{0.END_IF}").format(kw)
		expected_if_then_else = (
				"{0.IF} a {0.LE} b {0.THEN}\n"
				"\ta {0.ASSIGN} b\n"
				"{0.ELSE}\n"
				"\tb {0.ASSIGN} a\n"
				"{0.END_IF}").format(kw)
		condition = operators.LessOrEqual(None, _id("a"), _id("b"))
		then_block = _bogus_block("a", "b")
		else_block = _bogus_block("b", "a")
		if_then = statements.IfThenElse(None, condition, then_block)
		if_then_else = statements.IfThenElse(None, condition, then_block, else_block)
		self.assertEqual(if_then.lda_format(), expected_if_then)
		self.assertEqual(if_then_else.lda_format(), expected_if_then_else)

	def test_for(self):
		expected = (
				"{0.FOR} i {0.FROM} a {0.TO} b {0.DO}\n"
				"\tx {0.ASSIGN} y\n"
				"{0.END_FOR}").format(kw)
		body = _bogus_block("x", "y")
		for_loop = statements.For(None, _id("i"), _id("a"), _id("b"), body)
		self.assertEqual(for_loop.lda_format(), expected)

	def test_while(self):
		expected = (
				"{0.WHILE} {0.TRUE} {0.DO}\n"
				"\ta {0.ASSIGN} b\n"
				"{0.END_WHILE}").format(kw)
		body = _bogus_block("a", "b")
		while_loop = statements.While(None, expression.LiteralBoolean(None, True), body)
		self.assertEqual(while_loop.lda_format(), expected)

	def test_algorithm(self):
		expected = (
				"{0.ALGORITHM}\n"
				"{0.LEXICON}\n"
				"\ta : {0.INT}\n"
				"\tb : {0.INT}\n"
				"{0.BEGIN}\n"
				"\ta {0.ASSIGN} b\n"
				"{0.END}").format(kw)
		a = typedesc.Field(_id("a"), typedesc.Integer)
		b = typedesc.Field(_id("b"), typedesc.Integer)
		lexicon = typedesc.Lexicon([a, b])
		body = _bogus_block("a", "b")
		algorithm = module.Algorithm(None, lexicon, body)
		self.assertEqual(algorithm.lda_format(), expected)

	def test_function(self):
		expected = (
				"{0.FUNCTION} lolilol(param : {0.INT}): {0.INT}\n"
				"{0.LEXICON}\n"
				"\ta : {0.INT}\n"
				"\tb : {0.INT}\n"
				"{0.BEGIN}\n"
				"\ta {0.ASSIGN} b\n"
				"{0.END}").format(kw)
		name = _id("lolilol")
		params = [typedesc.Field(_id("param"), typedesc.Integer)]
		return_type = typedesc.Integer
		a = typedesc.Field(_id("a"), typedesc.Integer)
		b = typedesc.Field(_id("b"), typedesc.Integer)
		lexicon = typedesc.Lexicon([a, b])
		body = _bogus_block("a", "b")
		function_node = module.Function(None, name, params, return_type, lexicon, body)
		self.assertEqual(function_node.lda_format(), expected)

