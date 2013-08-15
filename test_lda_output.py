import unittest
import expression as expr
import keywords as kw
import module as modu
import statements as stat
import typedesc as type
import operators as ope

class test_lda_output(unittest.TestCase):
	def setUp(self):
		pass

		
	def _simple_return(self, test , resultat):
		self.assertEqual( test.lda_format(), resultat)

		
	def test_keyword(self):
		test = lambda t, r: self._simple_return(t, r)
		test(kw.INT, kw.INT.default_spelling)

		
	def test_type(self):
		test = lambda t, r: self._simple_return(t, r)
		#Scalar Type
		test(type.Integer, kw.INT.default_spelling)
		test(type.Real, kw.REAL.default_spelling)
		test(type.String, kw.STRING.default_spelling)
		test(type.Boolean, kw.BOOL.default_spelling)
		#Array
		test(type.ArrayType(type.Integer, 3), kw.INT.default_spelling + " : 3")
		#Composite
		test(type.CompositeType(
			type.Identifier(None, "Moule"), [
				type.Field(type.Identifier(None, "prix"),type.Integer),
				type.Field(type.Identifier(None, "nom"),type.String)
			]),
			"Moule = <prix : " + kw.INT.default_spelling + ", nom : " + kw.STRING.default_spelling +">")
		#Identifier
		test(type.Identifier(None, "ident"), "ident") 
		#Field
		test(type.Field(type.Identifier(None, "ident"), kw.INT), "ident : " + kw.INT.default_spelling)
		#Lexicon
		test(type.Lexicon(
			[type.Field(type.Identifier(None, "ident"), kw.INT)],
			[type.CompositeType(
				type.Identifier(None, "Moule"), [
					type.Field(type.Identifier(None, "prix"),type.Integer),
					type.Field(type.Identifier(None, "nom"),type.String)
				])
			]
			),
			kw.LEXICON.default_spelling 
			+ "\n\tident : " + kw.INT.default_spelling 
			+ "\n\tMoule = <prix : " + kw.INT.default_spelling + ", nom : " + kw.STRING.default_spelling +">" + "\n"
		)

		
	def test_expression(self):
		test = lambda t, r: self._simple_return(t, r)
		# Test _Literal
		test(expr.LiteralInteger(None, 1), 1)
		test(expr.LiteralReal(None, 1.1), 1.1)
		test(expr.LiteralString(None, "I am a string"), "I am a string")
		test(expr.LiteralBoolean(None, kw.TRUE), kw.TRUE.default_spelling)	
		# Test Varargs
		test(expr.Varargs(
			None, [
				type.Field(type.Identifier(None, "a"),type.Integer),
				type.Field(type.Identifier(None, "b"),type.String)
				]),
			"a : " + kw.INT.default_spelling + ", b : " + kw.STRING.default_spelling)
		

	def test_statements(self):
		test = lambda t, r: self._simple_return(t, r)
		#StatmentBlock
		test(stat.StatementBlock(
				None, ( [ope.Assignment ( 
					None, type.Identifier(None, "a"),
					type.Identifier(None, "b") ) ])
				),
			"a "+ kw.ASSIGN.default_spelling +" b\n")
		#IfThenElse
		test(
			stat.IfThenElse(None,
				ope.LessOrEqual(None,
						type.Identifier(None, "a"),
						type.Identifier(None, "b")
					),
				stat.StatementBlock(None,
					([ope.Assignment(None,
						type.Identifier(None, "a"),
						type.Identifier(None, "b")
					)])
				)
			),
			kw.IF.default_spelling + " a " + kw.LE.default_spelling + " b " + kw.THEN.default_spelling + "\n"
			+ "\ta " + kw.ASSIGN.default_spelling + " b" + "\n"
			+ kw.END_IF.default_spelling + "\n"
		)
		#For
		test(
			stat.For(None, type.Identifier(None, "i"), type.Identifier(None, "a"), type.Identifier(None, "b"),
				stat.StatementBlock(None,
					([ope.Assignment(None,
						type.Identifier(None, "x"),
						type.Identifier(None, "y")
					)])
				)
			),
			kw.FOR.default_spelling + " i " + kw.FROM.default_spelling + " a "  + kw.TO.default_spelling + " b " + kw.DO.default_spelling
			+ "\n\tx " + kw.ASSIGN.default_spelling + " y" + "\n" 
			+ kw.END_FOR.default_spelling + "\n"
		)
		#While
		test(
			stat.While(None,
				expr.LiteralBoolean(None, kw.TRUE),
				stat.StatementBlock(None,
					([ope.Assignment(None,
						type.Identifier(None, "a"),
						type.Identifier(None, "b")
					)])
				)
			),
			kw.WHILE.default_spelling + " " + kw.TRUE.default_spelling + " " + kw.DO.default_spelling + "\n"
			+ "\ta " + kw.ASSIGN.default_spelling + " b" + "\n"
			+ kw.END_WHILE.default_spelling + "\n"
		)
	
	
	def test_module(self):
		test = lambda t, r: self._simple_return(t, r)
		#Algorithme
		test(modu.Algorithm(None, 
			type.Lexicon(
				[type.Field(type.Identifier(None, "a"), kw.INT),
				 type.Field(type.Identifier(None, "b"), kw.INT)],
				[]
			),
			stat.StatementBlock(None,
			[ope.Assignment(None,
				type.Identifier(None, "a"),
				type.Identifier(None, "b")
				)
			])
		),
		kw.ALGORITHM.default_spelling + "\n" +
		kw.LEXICON.default_spelling + "\n" +
		"\ta : " + kw.INT.default_spelling + "\n" +
		"\tb : " + kw.INT.default_spelling + "\n\t\n" +
		kw.BEGIN.default_spelling + "\n" +
		"\ta " + kw.ASSIGN.default_spelling + " b" + "\n" +
		kw.END.default_spelling + "\n\n"
		)
			
		#Fonction
		test(modu.Function(None,
			type.Identifier(None, "lolilol"),
			[type.Field(type.Identifier(None, "param"), kw.INT)],
			type.Void,
			type.Lexicon(
				[type.Field(type.Identifier(None, "a"), kw.INT),
				 type.Field(type.Identifier(None, "b"), kw.INT)],
				[]
			),
			stat.StatementBlock(None,
			[ope.Assignment(None,
				type.Identifier(None, "a"),
				type.Identifier(None, "b")
				)
			])
		),
		kw.FUNCTION.default_spelling + " lolilol(param : " + kw.INT.default_spelling +")" + "\n" +
		kw.LEXICON.default_spelling + "\n" +
		"\ta : " + kw.INT.default_spelling + "\n" +
		"\tb : " + kw.INT.default_spelling + "\n\t\n" +
		kw.BEGIN.default_spelling + "\n" +
		"\ta " + kw.ASSIGN.default_spelling + " b" + "\n" +
		kw.END.default_spelling + "\n\n"
		)