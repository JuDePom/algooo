import ldakeywords as kw

class UnaryOp:
	right_ass = True

class BinaryOp:
	left_ass = True
	right_ass = False
	encompass = False

	def __init__(self, operator_token, lhs=None, rhs=None):
		self.operator_token = operator_token
		self.lhs = lhs
		self.rhs = rhs
	
	def __gt__(self, prev):
		return self.precedence > prev.precedence or \
				self.right_ass and self.precedence == prev.precedence

class RHSGlutton(BinaryOp):
	encompass = True

class ArraySubscript(RHSGlutton):
	keyword_def = kw.LSBRACK
	encompass_till = kw.RSBRACK
	encompass_several = True

class Addition(BinaryOp):
	keyword_def = kw.PLUS

class Assignment(BinaryOp):
	keyword_def = kw.ASSIGN
	right_ass = True

unary = []
binary_precedence = [
		[ArraySubscript],
		[],
		[],
		[Addition],
		[],
		[],
		[],
		[],
		[],
		[Assignment]
]
binary_flat = [opcls for sublist in binary_precedence for opcls in sublist]

unary_keyword_defs = [opcls.keyword_def for opcls in unary]
binary_keyword_defs = [opcls.keyword_def for opcls in binary_flat]

for i, group in enumerate(binary_precedence):
	group_id = len(binary_precedence) - i - 1
	for cls in group:
		cls.precedence = group_id
		print (group_id, cls.__name__)

