'''
Keyword lexicon.

For the sake of simplicity, "keywords" here refer to actual keywords and
miscellaneous symbols such as operators, comment markers, etc.

All keywords are given as lists of synonyms. This allows us to account for
common misspellings especially for words that are difficult to compose. For
example, while 'début' is the preferred way to spell the BEGIN keyword, we also
allow the unaccented 'debut'.

The first entry in each synonym list is the preferred spelling.
'''

ALGORITHM = ["algorithme"]
BEGIN = ["début", "debut"]
END = ["fin"]

MULTILINE_COMMENT_START = ["(*"]
MULTILINE_COMMENT_END = ["*)"]
SINGLELINE_COMMENT_START = ["//"]

