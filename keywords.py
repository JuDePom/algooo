import re

'''
Keyword lexicon.

For the sake of simplicity, "keywords" here refer to actual keywords and
miscellaneous symbols such as operators, comment markers, etc.

All keywords are given as lists (or tuples) of synonyms. This allows us to
account for common misspellings especially for words that are difficult to
compose. For example, while 'début' is the preferred way to spell the BEGIN
keyword, we also allow the unaccented 'debut'.

The first entry in each synonym list is the preferred spelling.
'''

class Keyword:
	'''
	Base class for keywords.

	There are different subclasses of keywords, because they shall not all be
	parsed according to the same rule.
	'''
	def __init__(self, *synonyms):
		self.default_spelling = synonyms[0]
		self.synonyms = synonyms

class AlphaKeyword(Keyword):
	'''
	Alphanumeric keyword.
	
	Alphanumeric keywords cannot be glued to one another and must be separated by
	at least one non-alphanumeric character.
	'''
	regexp = re.compile(r'^[^\d\W]\w*', re.UNICODE)

	def find(self, buf):
		match = AlphaKeyword.regexp.match(buf)
		if not match:
			return False
		found = match.group(0)
		return (found if found in self.synonyms else False)

class SymbolKeyword(Keyword):
	'''
	Non-alphanumeric symbolic keyword.

	Symbolic keywords may be strung together. E.g. this is a valid keyword
	sequence that will expand to two separate keywords: ()
	'''

	def __init__(self, *synonyms):
		self.default_spelling = synonyms[0]
		# sort synonyms by descending size so that longer synonyms get checked first
		# bogus example: if ".." is a synonym for ".", we need to check for ".." first
		self.synonyms = tuple(sorted(synonyms, key=len, reverse=True))

	def find(self, buf):
		for symbol in self.synonyms:
			if buf.startswith(symbol):
				return symbol
		return False


ALGORITHM      = AlphaKeyword("algorithme")
FUNCTION       = AlphaKeyword("fonction")
BEGIN          = AlphaKeyword("début", "debut")
END            = AlphaKeyword("fin")
RETURN         = AlphaKeyword("return")

FOR            = AlphaKeyword("pour")
FROM           = AlphaKeyword("de")
TO             = AlphaKeyword("jusque")
DO             = AlphaKeyword("faire")
END_FOR        = AlphaKeyword("fpour")

WHILE          = AlphaKeyword("tantque")
END_WHILE      = AlphaKeyword("ftantque", "ftant")

IF             = AlphaKeyword("si")
THEN           = AlphaKeyword("alors")
ELSE           = AlphaKeyword("sinon")
END_IF         = AlphaKeyword("fsi")

INOUT          = AlphaKeyword("inout")
ARRAY          = AlphaKeyword("tableau")
INT            = AlphaKeyword("entier")
REAL           = AlphaKeyword("réel", "reel")
BOOL           = AlphaKeyword("booléen", "booleen")
CHAR           = AlphaKeyword("caractère", "caractere")
STRING         = AlphaKeyword("chaîne", "chaine")

TRUE           = AlphaKeyword("vrai")
FALSE          = AlphaKeyword("faux")
NOT            = AlphaKeyword("non")

LPAREN         = SymbolKeyword("(")
RPAREN         = SymbolKeyword(")")
LSBRACK        = SymbolKeyword("[")
RSBRACK        = SymbolKeyword("]")
COLON          = SymbolKeyword(":")
COMMA          = SymbolKeyword(",")
TIMES          = SymbolKeyword("*")
PLUS           = SymbolKeyword("+")
MINUS          = SymbolKeyword("-")
SLASH          = SymbolKeyword("/")
QUOTE1         = SymbolKeyword("'")
QUOTE2         = SymbolKeyword("\"")
ASSIGN         = SymbolKeyword("\u2190", "<-")
LT             = SymbolKeyword("<")
GT             = SymbolKeyword(">")
LE             = SymbolKeyword("\u2264", "<=")
GE             = SymbolKeyword("\u2265", ">=")
EQ             = SymbolKeyword("=")
NE             = SymbolKeyword("\u2260", "!=")

MLC_START      = SymbolKeyword("(*")
MLC_END        = SymbolKeyword("*)")
SLC_START      = SymbolKeyword("//")


class meta:
	all_types = [ INT, REAL, BOOL, CHAR, STRING ]

