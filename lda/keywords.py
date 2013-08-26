import re

"""
Keyword lexicon.

For the sake of simplicity, "keywords" here refer to actual keywords and
miscellaneous strings representing operators, comment markers, etc.

All keywords are given as lists (or tuples) of synonyms. This allows us to
account for common misspellings especially for words that are difficult to
compose. For example, while 'début' is the preferred way to spell the BEGIN
keyword, we also allow the unaccented 'debut'.

The first entry in each synonym list is the preferred spelling.
"""

all_keywords = []
reserved = []

class Synonym:
	def __init__(self, word, keyword):
		self.word = word
		self.keyword = keyword
		assert (word == word.lower())
		self.gluable = not (word[0].isalpha() or word[0] == '_')
		self.give_way = []
		reserved.append(word)

class Keyword:
	def __init__(self, *synonyms):
		self.default_spelling = synonyms[0]
		self.synonyms = [Synonym(word, self) for word in synonyms]
		all_keywords.append(self)

	def __repr__(self):
		return self.default_spelling

	def lda(self, exp):
		exp.put(self.default_spelling)

ALGORITHM      = Keyword("algorithme")
FUNCTION       = Keyword("fonction")
LEXICON        = Keyword("lexique")
BEGIN          = Keyword("début", "debut")
END            = Keyword("fin")
RETURN         = Keyword("return")

FOR            = Keyword("pour")
FROM           = Keyword("de")
TO             = Keyword("jusque")
DO             = Keyword("faire")
END_FOR        = Keyword("fpour")

WHILE          = Keyword("tantque")
END_WHILE      = Keyword("ftantque", "ftant")

IF             = Keyword("si")
THEN           = Keyword("alors")
ELIF           = Keyword("snsi")
ELSE           = Keyword("sinon")
END_IF         = Keyword("fsi")

INOUT          = Keyword("inout")
ARRAY          = Keyword("tableau")
INT            = Keyword("entier")
REAL           = Keyword("réel", "reel")
BOOL           = Keyword("booléen", "booleen")
CHAR           = Keyword("caractère", "caractere")
STRING         = Keyword("chaîne", "chaine")

TRUE           = Keyword("vrai")
FALSE          = Keyword("faux")
NOT            = Keyword("non")
AND            = Keyword("et")
OR             = Keyword("ou")

LPAREN         = Keyword("(")
RPAREN         = Keyword(")")
LSBRACK        = Keyword("[")
RSBRACK        = Keyword("]")
COLON          = Keyword(":")
DOTDOT         = Keyword("..")
QUESTION_MARK  = Keyword("?")
COMMA          = Keyword(",")
DOT            = Keyword(".")
TIMES          = Keyword("*")
PLUS           = Keyword("+")
MINUS          = Keyword("-")
SLASH          = Keyword("/")
POWER          = Keyword("**")
MODULO         = Keyword("mod")
QUOTE1         = Keyword("'")
QUOTE2         = Keyword("\"")
ASSIGN         = Keyword("\u2190", "<-")
LT             = Keyword("<")
GT             = Keyword(">")
LE             = Keyword("\u2264", "<=")
GE             = Keyword("\u2265", ">=")
EQ             = Keyword("=")
NE             = Keyword("\u2260", "!=")
TRIPLE_STAR    = Keyword("***")

# Even though we're not using the comment keywords to actually skip the
# comments, these keywords still need to exist in order to ensure correct
# parsing priorities for other symbols.
MLC_START      = Keyword("(*")
MLC_END        = Keyword("*)")
SLC_START      = Keyword("//")

def _set_priorities():
	gluables = {}
	for k in all_keywords:
		gluables.update({s.word: s for s in k.synonyms if s.gluable})
	for word, syn in gluables.items():
		try:
			shorter = gluables[word[0:-1]]
			if shorter.keyword != syn.keyword and syn not in shorter.give_way:
				shorter.give_way.append(syn)
		except KeyError:
			pass

_set_priorities()

