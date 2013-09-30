import os, re, unittest
from lda.parser import Parser
from lda.errors import syntax, semantic
from lda.context import ContextStack
from lda.errors.handler import Logger
from lda import prettyprinter
from lda import kw
from fnmatch import fnmatch
from itertools import count
import subprocess


SNIPPETSDIR = os.path.join(os.path.dirname(__file__), "snippets")


# (*#ErrorClassExpectedRightAfterThisCommentEnds#*)
ERROR_REGEXP = re.compile(r"\(\*\#(.+?)(\#\*\))")

# (*% directive0, directive1 arg0 arg1 arg2, directive2 arg0 %*)
DIRECTIVE_REGEXP = re.compile(r"^\(\*\%\ (.*?)\ \%\*\)", re.DOTALL|re.MULTILINE)

# (%|expected output when running translated javascript %|)
OUTPUT_REGEXP = re.compile(r"^\(\*\|(?P<output>.*?)\|\*\)", re.DOTALL|re.MULTILINE)


class DefaultOptions:
	ignore_case        = False
	formals_in_lexicon = True


class TestSnippets(unittest.TestCase):
	def c(self, snippet):
		# ---- apply all directives ---------------
		options = DefaultOptions()
		directives_match = DIRECTIVE_REGEXP.match(snippet)
		if directives_match:
			for directive in directives_match.group(1).split(','):
				tokens = directive.split()
				self.assertEqual(2, len(tokens), tokens)
				k, v = tokens
				vtype = type(getattr(options, k))
				if vtype == bool:
					v = v == 'True'
				else:
					v = vtype(v)
				setattr(options, k, v)
		# ---- parse ------------------------------
		parser = Parser(options, raw_buf=snippet)
		logged_errors = []
		try:
			module = parser.analyze_module()
			self.assertTrue(parser.eof(), ("program couldn't be parsed entirely"
					" -- stopped at {}").format(parser.pos))
		except syntax.SyntaxError as e:
			logged_errors = [e]
		# ---- check ------------------------------
		if not logged_errors:
			logger = Logger()
			module.check(ContextStack(options), logger)
			logged_errors = list(logger.errors)
		# ---- match errors -----------------------
		snippet_errors = list(ERROR_REGEXP.finditer(snippet))
		# make sure the analysis raised as many errors as expected
		sc, lc = len(snippet_errors), len(logged_errors)
		self.assertEqual(sc, lc, "expected {} errors but {} were reported: {}"
				.format(sc, lc, logged_errors))
		# check each error
		start = 0
		for i, error, match in zip(count(), logged_errors, snippet_errors):
			classname = match.group(1)
			if classname.startswith('kw:'):
				class_ = syntax.ExpectedKeyword
			else:
				class_ = getattr(syntax, classname, None) or getattr(semantic, classname)
				self.assertIsNotNone(class_, "unknown error class: '{}'".format(classname))
			self.assertIsInstance(error, class_,
					"wrong error found at error marker #{}".format(i))
			self.assertEqual(error.pos.char, match.end(2),
					"error #{} wasn't reported at expected position (raised: {})"
					.format(i, error))
			if class_ is syntax.ExpectedKeyword:
				raw_kws = classname[1+classname.find(':'):].split(',')
				expected_keywords = set(getattr(kw, r) for r in raw_kws)
				self.assertSetEqual(expected_keywords, set(error.expected_keywords))
		# ---- stop there if there were any errors -------------
		if snippet_errors:
			return
		# ---- compile to LDA -----------------------
		#TODO pp = prettyprinter.LDAPrettyPrinter()
		#module.lda(pp)
		# TODO check for LDA equality with original snippet string
		# ---- compile to JS -----------------------
		pp = prettyprinter.JSPrettyPrinter()
		module.js(pp)
		# ---- run JS -------------------------
		if not module.algorithms:
			return
		code = "require('lda.js');\n\n{}\n\nP.main();\n".format(pp)
		shutup = False
		gotten_output = subprocess.check_output(["node", "-e", code],
				stderr = shutup and subprocess.DEVNULL or None,
				env={'NODE_PATH':'./jsruntime'}, universal_newlines=True
				).strip()
		output_match = OUTPUT_REGEXP.match(snippet)
		if output_match:
			snippet_output = output_match.group('output').strip()
		else:
			snippet_output = ''
		self.assertEqual(snippet_output, gotten_output.strip())


for fn in sorted(os.listdir(SNIPPETSDIR)):
	if not fnmatch(fn, '*.lda'):
		continue
	snipname = fn[:-4]
	path = os.path.join(SNIPPETSDIR, fn)
	with open(path, 'rt', encoding='utf8') as snippet_file:
		fbuf = snippet_file.read()
	test = lambda self, snippet=fbuf: self.c(snippet)
	test.__name__ = "test snippet '{}'".format(snipname)
	setattr(TestSnippets, test.__name__, test)

