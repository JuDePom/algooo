#!/usr/bin/python3

'''
LDA compiler entry point.
'''

import lda.parser
import lda.errors
import lda.context
import lda.prettyprinter
import argparse
import sys

ap = argparse.ArgumentParser(
	description="Compilateur de LDA (langage de description d'algorithme)")

ap.add_argument('path',
		metavar='LDA',
		help="chemin vers un fichier LDA")

ap.add_argument('--format', '-f',
		default='js',
		help="format de sortie")

ap.add_argument('--output-file', '-o',
		help="""fichier de sortie.
		Si omis, le résultat sera émis sur stdout.""")

ap.add_argument('--no-output', '-n', action='store_true',
		help="""vérifie uniquement la cohérence syntaxique et sémantique
		sans générer de code""")

ap.add_argument('--case-insensitive', action='store_true',
		help="""Ignorer la casse dans les identificateurs et les mot-clés""")

ap.add_argument('--js-standalone', '-s', action='store_true',
		help="""Si le format de sortie est `js`, faire que le script puisse
		être exécuté tel quel.""")

args = ap.parse_args()

parser = lda.parser.Parser(args, path=args.path)

try:
	module = parser.analyze_module()
except lda.errors.syntax.SyntaxError as e:
	print(e.pretty(parser.raw_buf), file=sys.stderr)
	sys.exit(1)

logger = lda.errors.handler.Logger()
module.check(lda.context.ContextStack(), logger)

if logger:
	for e in logger.errors:
		print(e.pretty(parser.raw_buf), file=sys.stderr)
	sys.exit(1)

if args.no_output:
	sys.exit(0)

if args.format == 'lda':
	pp = lda.prettyprinter.LDAPrettyPrinter()
	module.lda(pp)
	output = str(pp)
elif args.format == 'js':
	pp = lda.prettyprinter.JSPrettyPrinter()
	module.js(pp)
	output = str(pp)
	if args.js_standalone:
		output = "require('lda.js');\n\n{}\n\nP.main();\n".format(output)
else:
	raise Exception("Format de sortie inconnu : " + args.format)

if args.output_file is None:
	print(output)
else:
	with open(args.output_file, 'wt', encoding='utf8') as output_file:
		output_file.write(output)

