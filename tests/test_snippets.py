"""
LDA code snippet torture test. Run a number of tests on every *.lda file
in the `snippets` directory.

You can also call this script from the command line in the following fashion to
test one snippet at a time:
	python -m tests.test_snippets SNIPPETNAME

The snippets may either be:
- incorrect, to test the compiler's error reporting system; the expected errors
must be specified as specially-formatted comments in the snippet; or
- correct, to test the compiler's compliance with a specific language construct,
and/or to ensure a snippet behaves correctly; the expected output of the program
must be specified as a specially-formatted comment in the snippet.

Each snippet is subjected to the following tests:
- Preprocess snippet file by reading directives in comments (options, expected
output, expected errors...).
- Parse (lexical/syntactic analysis) and Check (semantic analysis); ensure the
raised errors match those specified in the comments; if there are no errors and
we weren't expecting any, keep going.
- Compile to JS.
- Compile to LDA and then back to JS; ensure this JS version is identical to
the one obtained above.
- Run JS and ensure the JS output matches that defined in the snippet's comments
"""

import os
import re
import unittest
import sys
from fnmatch import fnmatch
from itertools import count

from tests import jsshell

from lda.parser import Parser
from lda.errors import syntax, semantic
from lda.context import ContextStack
from lda.errors.handler import Logger
from lda import prettyprinter
from lda import kw


SNIPPETSDIR = os.path.join(os.path.dirname(__file__), "snippets")


# (*#ErrorClassExpectedRightAfterThisCommentEnds#*)
ERROR_REGEXP = re.compile(r"\(\*#(.+?)(#\*\))")

# (*% directive0, directive1 arg0 arg1 arg2, directive2 arg0 %*)
DIRECTIVE_REGEXP = re.compile(r"^\(\*% ?(.*?) ?%\*\)", re.DOTALL | re.MULTILINE)

# Non-interactive program:
#     (*|expected output when running translated javascript|*)
# Interactive program:
#     (*|output 1 | keyboard input 1 | output2 | keyboard input 2 | output 3 |*)
SESSION_REGEXP = re.compile(r"^\(\*\|(?P<session>.*?)\|\*\)", re.DOTALL | re.MULTILINE)


class DefaultOptions:
	ignore_case        = False


class TestSnippets(unittest.TestCase):
	def c(self, snippet):
		# TODO this is a hellish monstrosity
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
		# ---- parse & check ----------------------
		try:
			parser = Parser(options, raw_buf=snippet)
			module = parser.analyze_module()
			self.assertTrue(parser.eof(), ("program couldn't be parsed entirely"
					" -- stopped at {}").format(parser.pos))
		except syntax.SyntaxError as e:
			logged_errors = [e]
		else:
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
		# ---- compile to JS directly ----------------
		jspp = prettyprinter.JSPrettyPrinter()
		module.js(jspp)
		js1 = str(jspp)
		# ---- compile to JS through regenerated LDA -----------
		ldapp = prettyprinter.LDAPrettyPrinter()
		module.lda(ldapp)
		regenerated = str(ldapp)
		jspp = prettyprinter.JSPrettyPrinter()
		module2 = Parser(options, raw_buf=regenerated).analyze_module()
		module2.check(ContextStack(options), logger)
		module2.js(jspp)
		js2 = str(jspp)
		# ---- both JS versions of the same program must end up identical
		# Instead of jumping through these hoops (LDA->LDA->JS), we could've
		# compared the original program with the regenerated LDA code, but then
		# we'd have to keep track of comments, whitespace, etc. In other words,
		# a ton of work for very little benefit.
		self.assertEqual(js1, js2)
		# ---- run JS -------------------------
		if not module.algorithms:
			return
		session_match = SESSION_REGEXP.match(snippet)
		if session_match:
			fragments = session_match.group('session').strip().split('|')
			snippet_output = ' '.join(f.strip() for f in fragments[0::2])
			snippet_input = '\n'.join(f.strip() for f in fragments[1::2])
		else:
			snippet_output = ''
			snippet_input = ''
		gotten_output = jsshell.run(js1, snippet_input)
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

if __name__ == '__main__':
	getattr(TestSnippets(), "test snippet '{}'".format(sys.argv[1]))()

