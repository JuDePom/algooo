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
ap.add_argument('path', metavar='LDA', help="chemin vers un fichier LDA")
ap.add_argument('--format', '-f', default='js', help="format de sortie")
ap.add_argument('--output-file', '-o', help="fichier de sortie. \
		Si omis, le résultat sera émis sur stdout.")
ap.add_argument('--no-output', '-n', action='store_true',
		help="vérifie uniquement la cohérence syntaxique et sémantique \
		sans générer de code")

args = ap.parse_args()

parser = lda.parser.Parser(args.path)

try:
	module = parser.analyze_module()
except errors.LDASyntaxError:
	error = parser.syntax_errors[-1]
	print(error, file=sys.stderr)
	sys.exit(1)

print (" * Syntaxe : OK.")

module.check()

print (" * Sémantique : OK.")

if args.no_output:
	sys.exit(0)

if args.format == 'dot':
	from lda import dot
	output = lda.dot.format(module)
elif args.format == 'lda':
	output = module.lda_format()
elif args.format == 'js':
	output = module.js_format()
else:
	raise Exception("Format de sortie inconnu : " + args.format)

if args.output_file is None:
	print(output)
else:
	with open(args.output_file, 'wt', encoding='utf8') as output_file:
		output_file.write(output)

