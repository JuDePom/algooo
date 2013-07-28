'''
LDA compiler entry point.
'''

import sys
import parser

if __name__ == '__main__':
	p = parser.Parser(sys.argv[1])
	top = p.analyze_top_level()
	# quick & dirty output of the tree
	for thing in top:
		print("----------------------")
		print(str(thing))
		

