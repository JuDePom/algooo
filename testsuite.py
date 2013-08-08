#!/usr/bin/python3

import ldaparser
import symboltable
import errors
import traceback

unexpected = 0

def printred(*stuff):
	print('\033[91m', end='')
	print(*stuff, end='\033[0m\n')

def print_error(buf, reason, print_traceback=True):
	printred("[ERROR] with test:", buf)
	printred("....... reason:", reason)
	printred(".......")
	if print_traceback:
		for line in traceback.format_exc().split('\n'):
			printred(".......", line)

def parse(analysis_name, buf, context=symboltable.SymbolTable()):
	p = ldaparser.Parser(path=None, buf=buf)
	p.advance()
	return getattr(p, 'analyze_' + analysis_name)(), p

def passtest(analysis_name, buf, context=symboltable.SymbolTable(),
		forward=False):
	try:
		node, parser = parse(analysis_name, buf, context)
		if not parser.eof():
			raise errors.LDAError("On aurait dû atteindre l'EOF !")
		node.check(context)
		print ("[OK] passed:", buf)
		return
	except errors.LDAError as e:
		if forward:
			raise e
		print_error(buf, "failed but should have PASSED")
	except Exception as e:
		caught = e
		print_error(buf, "non-LDA error! should never happen!")
	global unexpected
	unexpected += 1

def failtest(analysis_name, buf, context=symboltable.SymbolTable()):
	try:
		passtest(analysis_name, buf, context, True)
		print_error(buf, "passed but should have FAILED", False)
		global unexpected
		unexpected += 1
	except errors.LDAError as e:
		print ("[OK] failed: {} \t(because: {})".format(buf, e))



lex, _ = parse('lexicon', """
		lexique
			Moule=<a:entier, b:chaîne>
			m:Moule
			t1:tableau Moule[0..2]
			t2:tableau Moule[0..2,0..2]""")


#######################################################################

expressions = [
		'1', '1.', '.1',
		'+1', '+ 1',
		'-1', '- 1',
		'+1.0',
		'+-+++--+ ++-+ -+++--- - +1',
		'+-+++--+ ++-+ -+++--- - +.24',
		'1 + 1', '1+1', '1+ 1', '1 +1',
		'1 - 1',
		'1 * 1',
		'1 / 1',
		'1 mod 1',
		'1+m.a', '1+m.      a', '1+m     .a', '1+m . a',
		'1+t1[0].a',
		't1[m.a]',
		't1[t1[0].a]',
		'm.a + t1[0].a',
]

for e in expressions:
	passtest('expression', e, lex)

#######################################################################

expressions = [
		'.', '0.0.', '0..', '0.0..', '0...',
		'1 +', '1+',
		'1 -', '1-',
		'1 *', '1*',
		'1 /', '1/',
		'1 mod',
		'1mod 1', '1mod1', '1 mod1',
		'1+m. .a',
		#'1+m..a',
		'"bla"+m.a',
		#'m..m',
		't1[1,2,3,4,5,6,7,8,9]',
		't1[1.]',
		't1["a"]',
		't1[m.b]',
		't1[m.dskfjkgsfdhkgurthi]',
]

for e in expressions:
	failtest('expression', e, lex)

######################################################################

print ("finished all tests -", unexpected, "errors")

