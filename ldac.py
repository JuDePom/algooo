#!/usr/bin/env python3

"""
LDA compiler command line front-end.
"""

from lda import build_tree, translate_tree, CompilationFailed
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

ap.add_argument('--ignore-case', '-c', action='store_true',
		help="""Ignorer la casse dans les identificateurs et les mot-clés""")

ap.add_argument('--execute', '-x', action='store_true',
		help="""Exécuter le programme immédiatement s'il ne contient
		aucune erreur""")

args = ap.parse_args()

args.extra_js_code = "P.main();"
args.stats_comment = True

try:
	module = build_tree(args, None, args.path)
except CompilationFailed as cf:
	for error in cf.errors:
		print(error.pretty(cf.buf), file=sys.stderr)
	sys.exit(1)
if args.no_output:
	sys.exit(0)
code = translate_tree(args, module, args.format)
if args.execute:
	assert args.format == 'js', "on ne peut exécuter que du JavaScript !"
	import jsshell
	jsshell.run_interactive(code)
elif args.output_file:
	with open(args.output_file, 'wt', encoding='utf8') as f:
		f.write(code)
else:
	print(code)
