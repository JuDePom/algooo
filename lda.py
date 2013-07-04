'''
LDA compiler entry point.
'''

import sys
import parser

if __name__ == '__main__':
	p = parser.Parser(sys.argv[1])
	p.analyze_algorithm()

