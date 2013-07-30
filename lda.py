'''
LDA compiler entry point.
'''

import sys
import parser

class Affichage:
	@staticmethod
	def affichage_arbre(arbre):
		padding = 0
		last = None
		for x in (str(arbre)).split("\n"):
			start=0
		
			if x[0] == '[':
				start=1
				padding += 1
			if x[0] == ']':
				start=1
				padding -= 1
			if x[0] == ',':
				start=2
			
			for i in range(0, padding):
				sys.stdout.write("|   ")
			print(x[start:])
		


if __name__ == '__main__':
	p = parser.Parser(sys.argv[1])
	top = p.analyze_top_level()
	# quick & dirty output of the tree
	for thing in top:
		print("----------------------")
		Affichage.affichage_arbre(thing)
		
		


