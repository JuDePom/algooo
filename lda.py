#!/usr/bin/python3

'''
LDA compiler entry point.
'''

import ldaparser
import argparse

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

parser = ldaparser.Parser(args.path)
module = parser.analyze_module()
print (" * Syntaxe : OK.")
module.check()
print (" * Sémantique : OK.")

if not args.no_output:
	if   args.format == 'quick': import quick as formatter
	elif args.format == 'dot'  : import dot   as formatter
	elif args.format == 'js'   : import js    as formatter
	else:
		raise Exception("Format de sortie inconnu : " + args.format)

	output = formatter.format_tree(module)

	if args.output_file is None:
		print (output)
	else:
		with open(args.output_file, 'wt', encoding='utf8') as output_file:
			output_file.write(output)

try:
	ldaparser.analyze_top_level() 
except (LDASyntaxError):
	print (message)
