#!/usr/bin/python3

'''
LDA compiler entry point.
'''

import lda.parser
import lda.errors
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

args = ap.parse_args()

parser = lda.parser.Parser(args, path=args.path)

try:
	module = parser.analyze_module()
except lda.errors.syntax.SyntaxError as ex:
	print(parser.relevant_syntax_error, file=sys.stderr)
	sys.exit(1)

print (" * Syntaxe : OK.")

logger = lda.errors.handler.Logger()
module.check({}, logger)

if logger:
	print (" *** ERREURS DE SÉMANTIQUE", file=sys.stderr)
	for e in logger.errors:
		if e.relevant:
			print(e, file=sys.stderr)
	sys.exit(1)
else:
	print (" * Sémantique : OK.")

if args.no_output:
	sys.exit(0)

if args.format == 'dot':
	from lda import dot
	output = lda.dot.format(module)
elif args.format == 'lda':
	from lda import ldaexporter
	exp = lda.ldaexporter.LDAExporter()
	module.lda(exp)
	output = str(exp)
elif args.format == 'js':
	from lda import jsexporter
	exp = lda.jsexporter.JSExporter()
	module.js(exp)
	output = str(exp)
else:
	raise Exception("Format de sortie inconnu : " + args.format)

if args.output_file is None:
	print(output)
else:
	with open(args.output_file, 'wt', encoding='utf8') as output_file:
		output_file.write(output)

