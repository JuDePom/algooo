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
	List of all SymbolKeywordDef objects declared in this module.
	'''
	all_symbols = []

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
	regexp = re.compile(r'[^\d\W]\w*', re.UNICODE)

	def find(self, buf, pos):
		match = AlphaKeywordDef.regexp.match(buf, pos)
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

	def __init__(self, *synonyms):
		self.give_way = [] # List of SymbolKeywordDefs that must be checked before
		                   # self. Will be populated at the end of the module.
		self.default_spelling = synonyms[0]
		# sort synonyms by descending size so that longer synonyms get checked first
		# bogus example: if ".." is a synonym for ".", we need to check for ".." first
		self.synonyms = tuple(sorted(synonyms, key=len, reverse=True))
		meta.all_symbols.append(self)

	def must_give_way(self, other):
		'''
		Return True if the presence of other must be checked before the presence
		of self in the input stream.

		For example, if << and < exist as distinct keywords, then the presence of
		<< shall be checked before the presence of < to limit keyword conflicts.
		'''
		for mine in self.synonyms:
			for theirs in other.synonyms:
				if theirs.startswith(mine):
					return True
		return False

	def find(self, buf, pos):
		for priority in self.give_way:
			if priority.find(buf, pos):
				return
		for symbol in self.synonyms:
			if buf.startswith(symbol, pos):
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

# Even though we're not using the comment keywords to actually skip the
# comments, these keywords still need to exist in order to ensure correct
# parsing priorities for other symbols.
MLC_START      = SymbolKeywordDef("(*")
MLC_END        = SymbolKeywordDef("*)")
SLC_START      = SymbolKeywordDef("//")

# build give_way lists
# TODO: écrémer ... si * gw ** gw ***, alors * gw *** est redondant et *** sera vérifié une fois de trop
for i, a in enumerate(meta.all_symbols):
	for b in meta.all_symbols[i+1:]:
		if a.must_give_way(b):
			a.give_way.append(b)
		elif b.must_give_way(a):
			b.give_way.append(a)
