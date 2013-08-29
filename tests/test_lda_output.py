from tests.ldatestcase import LDATestCase
from lda import kw, module, expression, statements, operators, ldaexporter
from lda.symbols import Lexicon

class test_lda_output(LDATestCase):
	def _assert_export(self, cls, program):
		stmt = self.analyze(cls, program)
		exp = ldaexporter.LDAExporter()
		stmt.lda(exp)
		self.assertEqual(str(exp), program)

	def test_lexicon(self):
		program = (
				"{kw.LEXICON}\n"
				"\tMoule = <prix: {kw.INT}, nom: {kw.STRING}>\n"
				"\ttab: tableau Moule[0 .. i, 0 .. j]").format(kw=kw)
		self._assert_export(Lexicon, program)

	def test_literals(self):
		self._assert_export(expression.LiteralInteger, "1")
		self._assert_export(expression.LiteralReal, "1.1")
		self._assert_export(expression.LiteralReal, "0.1")
		self._assert_export(expression.LiteralString, "\"bonjour\"")
		self._assert_export(expression.LiteralBoolean, "vrai")
		self._assert_export(expression.LiteralBoolean, "faux")
		self._assert_export(expression.LiteralCharacter, "'a'")

	def test_if(self):
		program = (
				"{kw.IF} a {kw.LE} b {kw.THEN}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.END_IF}").format(kw=kw)
		self._assert_export(statements.If, program)

	def test_if_else(self):
		program = (
				"{kw.IF} a {kw.LE} b {kw.THEN}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.ELSE}\n"
				"\tb {kw.ASSIGN} a\n"
				"{kw.END_IF}").format(kw=kw)
		self._assert_export(statements.If, program)

	def test_if_elif_else(self):
		program = (
				"{kw.IF} a {kw.LE} b {kw.THEN}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.ELIF} b {kw.LE} c {kw.THEN}\n"
				"\tb {kw.ASSIGN} c\n"
				"{kw.ELIF} c {kw.LE} d {kw.THEN}\n"
				"\tc {kw.ASSIGN} d\n"
				"{kw.ELSE}\n"
				"\tb {kw.ASSIGN} a\n"
				"{kw.END_IF}").format(kw=kw)
		self._assert_export(statements.If, program)

	def test_for(self):
		program = (
				"{kw.FOR} i {kw.FROM} a {kw.TO} b {kw.DO}\n"
				"\tx {kw.ASSIGN} y\n"
				"{kw.END_FOR}").format(kw=kw)
		self._assert_export(statements.For, program)

	def test_while(self):
		program = (
				"{kw.WHILE} {kw.TRUE} {kw.DO}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.END_WHILE}").format(kw=kw)
		self._assert_export(statements.While, program)

	def test_algorithm(self):
		program = (
				"{kw.ALGORITHM}\n"
				"{kw.LEXICON}\n"
				"\ta: {kw.INT}\n"
				"\tb: {kw.INT}\n"
				"{kw.BEGIN}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.END}").format(kw=kw)
		self._assert_export(module.Algorithm, program)

	def test_function(self):
		program = (
				"{kw.FUNCTION} lolilol(param1: {kw.INT}, param2: {kw.INT}): {kw.INT}\n"
				"{kw.LEXICON}\n"
				"\ta: {kw.INT}\n"
				"\tb: {kw.INT}\n"
				"{kw.BEGIN}\n"
				"\ta {kw.ASSIGN} b\n"
				"{kw.END}").format(kw=kw)
		self._assert_export(module.Function, program)

	def test_empty_function(self):
		program = "{kw.FUNCTION} vide()\n{kw.BEGIN}\n{kw.END}".format(kw=kw)
		self._assert_export(module.Function, program)

	def test_empty_while(self):
		program = "{kw.WHILE} {kw.TRUE} {kw.DO}\n{kw.END_WHILE}".format(kw=kw)
		self._assert_export(statements.While, program)

	def test_empty_for(self):
		program = "{kw.FOR} i {kw.FROM} 0 {kw.TO} 10 {kw.DO}\n{kw.END_FOR}".format(kw=kw)
		self._assert_export(statements.For, program)

	def test_complex_indentation(self):
		program = (
				"{kw.LEXICON}\n"
				"\tDate = <j: entier, m: entier, a: entier>\n"
				"\n"
				"\n"
				"{kw.ALGORITHM}\n"
				"{kw.LEXICON}\n"
				"\td: Date\n"
				"\te: entier\n"
				"{kw.BEGIN}\n"
				"\t{kw.IF} {kw.FALSE} {kw.THEN}\n"
				"\t\te {kw.ASSIGN} 3\n"
				"\t\t{kw.WHILE} e {kw.LT} 10 {kw.DO}\n"
				"\t\t\te {kw.ASSIGN} e + 1\n"
				"\t\t{kw.END_WHILE}\n"
				"\t{kw.ELIF} {kw.TRUE} {kw.THEN}\n"
				"\t\te {kw.ASSIGN} 12\n"
				"\t{kw.ELSE}\n"
				"\t\te {kw.ASSIGN} -1\n"
				"\t{kw.END_IF}\n"
				"\td.j {kw.ASSIGN} e\n"
				"{kw.END}\n").format(kw=kw)
		self._assert_export(module.Module, program)

