import ldakeywords as kw
import dot

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
	
	def part_of_rhs(self, whose):
		return self.precedence > whose.precedence or \
			(self.right_ass and self.precedence == whose.precedence)
	
	def put_node(self, cluster):
		op_node = dot.Node(self.keyword_def.default_spelling,
				cluster,
				self.lhs.put_node(cluster),
				self.rhs.put_node(cluster))
		op_node.shape = "circle"
		return op_node

class RHSGlutton(BinaryOp):
	encompass = True

class ArraySubscript(RHSGlutton):
	keyword_def = kw.LSBRACK
	encompass_till = kw.RSBRACK
	encompass_several = True

class Multiplication(BinaryOp):
	keyword_def = kw.TIMES

class Addition(BinaryOp):
	keyword_def = kw.PLUS

class Assignment(BinaryOp):
	keyword_def = kw.ASSIGN
	right_ass = True
	
	def check(self, context):
		# TODO
		print(":)")

unary = []
binary_precedence = [
		[ArraySubscript],
		[],
		[Multiplication],
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

