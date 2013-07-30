'''
LDA compiler entry point.
'''

import sys
import parser

def pretty_tree(arbre):
	padding = 0
	for x in (str(arbre)).split("\n"):
		start = 0
		if x[0] == '[':
			start = 1
			padding += 1
		elif x[0] == ']':
			start=1
			padding -= 1
		elif x[0] == ',':
			start=2
		for i in range(0, padding):
			sys.stdout.write("|   ")
		print(x[start:])

if __name__ == '__main__':
	p = parser.Parser(sys.argv[1])
	top = p.analyze_top_level()
	for thing in top:
		pretty_tree(thing)

