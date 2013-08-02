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

class meta:
	'''
	Additional information about keywords.
	'''

	''' 
	List of all spellings of every keyword. 
	Useful to check for keyword infringement on a string.
	'''
	all_keywords = []

	'''
	List of all keywords denoting an LDA scalar type.
	'''
	all_scalar_types = []

class KeywordDef:
	'''
	Base class for keywords.

	There are different subclasses of keywords, because they shall not all be
	parsed according to the same rule.
	'''

	def __init__(self, *synonyms):
		self.default_spelling = synonyms[0]
		self.synonyms = synonyms
		meta.all_keywords.extend(synonyms)
	
	def __repr__(self):
		return "k_" + self.default_spelling

class AlphaKeywordDef(KeywordDef):
	'''
	Alphanumeric keyword.
	
	Alphanumeric keywords cannot be glued to one another and must be separated by
	at least one non-alphanumeric character.
	'''
	regexp = re.compile(r'^[^\d\W]\w*', re.UNICODE)

	def find(self, buf):
		match = AlphaKeywordDef.regexp.match(buf)
		if match is None:
			return
		found = match.group(0)
		if found in self.synonyms:
			return found

class SymbolKeywordDef(KeywordDef):
	'''
	Non-alphanumeric symbolic keyword.

	Symbolic keywords may be strung together. E.g. this is a valid keyword
	sequence that will expand to two separate keywords: ()
	'''

	parsing_order = []

	def __init__(self, *synonyms):
		self.default_spelling = synonyms[0]
		# sort synonyms by descending size so that longer synonyms get checked first
		# bogus example: if ".." is a synonym for ".", we need to check for ".." first
		self.synonyms = tuple(sorted(synonyms, key=len, reverse=True))

	def find(self, buf):
		for symbol in self.synonyms:
			if buf.startswith(symbol):
				return symbol


ALGORITHM      = AlphaKeywordDef("algorithme")
FUNCTION       = AlphaKeywordDef("fonction")
LEXICON        = AlphaKeywordDef("lexique")
BEGIN          = AlphaKeywordDef("début", "debut")
END            = AlphaKeywordDef("fin")
RETURN         = AlphaKeywordDef("return")

FOR            = AlphaKeywordDef("pour")
FROM           = AlphaKeywordDef("de")
TO             = AlphaKeywordDef("jusque")
DO             = AlphaKeywordDef("faire")
END_FOR        = AlphaKeywordDef("fpour")

WHILE          = AlphaKeywordDef("tantque")
END_WHILE      = AlphaKeywordDef("ftantque", "ftant")

IF             = AlphaKeywordDef("si")
THEN           = AlphaKeywordDef("alors")
ELSE           = AlphaKeywordDef("sinon")
END_IF         = AlphaKeywordDef("fsi")

INOUT          = AlphaKeywordDef("inout")
ARRAY          = AlphaKeywordDef("tableau")
INT            = AlphaKeywordDef("entier")
REAL           = AlphaKeywordDef("réel", "reel")
BOOL           = AlphaKeywordDef("booléen", "booleen")
CHAR           = AlphaKeywordDef("caractère", "caractere")
STRING         = AlphaKeywordDef("chaîne", "chaine")

TRUE           = AlphaKeywordDef("vrai")
FALSE          = AlphaKeywordDef("faux")
NOT            = AlphaKeywordDef("non")
AND            = AlphaKeywordDef("et")
OR             = AlphaKeywordDef("ou")

LPAREN         = SymbolKeywordDef("(")
RPAREN         = SymbolKeywordDef(")")
LSBRACK        = SymbolKeywordDef("[")
RSBRACK        = SymbolKeywordDef("]")
COLON          = SymbolKeywordDef(":")
DOTDOT         = SymbolKeywordDef("..")
COMMA          = SymbolKeywordDef(",")
DOT            = SymbolKeywordDef(".")
TIMES          = SymbolKeywordDef("*")
PLUS           = SymbolKeywordDef("+")
MINUS          = SymbolKeywordDef("-")
SLASH          = SymbolKeywordDef("/")
POWER          = SymbolKeywordDef("**")
MODULO         = AlphaKeywordDef("mod")
QUOTE1         = SymbolKeywordDef("'")
QUOTE2         = SymbolKeywordDef("\"")
ASSIGN         = SymbolKeywordDef("\u2190", "<-")
LT             = SymbolKeywordDef("<")
GT             = SymbolKeywordDef(">")
LE             = SymbolKeywordDef("\u2264", "<=")
GE             = SymbolKeywordDef("\u2265", ">=")
EQ             = SymbolKeywordDef("=")
NE             = SymbolKeywordDef("\u2260", "!=")

MLC_START      = SymbolKeywordDef("(*")
MLC_END        = SymbolKeywordDef("*)")
SLC_START      = SymbolKeywordDef("//")

meta.all_scalar_types = [ INT, REAL, BOOL, CHAR, STRING ]

