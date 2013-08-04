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
ap.add_argument('--output', '-o', help="fichier de sortie. \
		Si omis, le résultat sera émis sur stdout.")

args = ap.parse_args()

if   args.format == 'quick': import quick as formatter
elif args.format == 'dot'  : import dot   as formatter
elif args.format == 'js'   : import js    as formatter
else:
	raise Exception("Format de sortie inconnu : " + args.format)

parser = ldaparser.Parser(args.path)
top    = parser.analyze_top_level()
output = formatter.format_tree(top)

if args.output is None:
	print (output)
else:
	with open(args.output, 'wt', encoding='utf8') as outfile:
		outfile.write(output)

