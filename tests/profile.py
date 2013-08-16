#!/usr/bin/python3

import lda.parser
import sys
import cProfile

count = int(sys.argv[1])
path = sys.argv[2]

print ("#### PROFIL : PARSER {}, {} FOIS ####".format(path, count))

p = lda.parser.Parser(path)

def doit():
	for i in range(count):
		p.reset_pos()
		p.analyze_module()

cProfile.run("doit()", sort="time")

