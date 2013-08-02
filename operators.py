import ldakeywords as kw

_highest_pg = 100
_current_pg = _highest_pg
def _new_precedence_group():
	global _current_pg
	_current_pg -= 1

class meta:
	all_unaries = []
	all_binaries = []

class OpDef:
	def __init__(self, symbol, precedence=None, unary=False,\
	             right_ass=False, encompass_till=None):
		if precedence is None:
			# we can't put _current_pg as the default value for precedence
			# because it's not resolved at runtime...
			precedence = _current_pg
		self.precedence     = precedence
		self.symbol         = symbol
		self.unary          = unary 
		self.right_ass      = right_ass
		self.encompass_till = encompass_till
		self.binary         = not unary
		self.left_ass       = not right_ass
		if self.binary:
			meta.all_binaries.append(self)
		else:
			meta.all_unaries.append(self)

	def __repr__(self):
		return str(self.symbol)


_new_precedence_group()
SUBSCRIPT      = OpDef(kw.LSBRACK, encompass_till=kw.RSBRACK)
MEMBER_SELECT  = OpDef(kw.DOT)
UNARY_MINUS    = OpDef(kw.MINUS, unary=True, right_ass=True)
UNARY_PLUS     = OpDef(kw.PLUS, unary=True, right_ass=True)
NOT            = OpDef(kw.NOT, unary=True, right_ass=True)

_new_precedence_group()
POWER          = OpDef(kw.POWER, right_ass=True)

_new_precedence_group()
MULTIPLICATION = OpDef(kw.TIMES)
DIVISION       = OpDef(kw.SLASH)
MODULO         = OpDef(kw.MODULO)

_new_precedence_group()
SUBTRACTION    = OpDef(kw.MINUS)
ADDITION       = OpDef(kw.PLUS)

_new_precedence_group()
RANGE          = OpDef(kw.DOTDOT)

_new_precedence_group()
LT             = OpDef(kw.LT)
GT             = OpDef(kw.GT)
LE             = OpDef(kw.LE)
GE             = OpDef(kw.GE)

_new_precedence_group()
EQ             = OpDef(kw.EQ)
NE             = OpDef(kw.NE)

_new_precedence_group()
AND            = OpDef(kw.AND)

_new_precedence_group()
OR             = OpDef(kw.OR)

_new_precedence_group()
ASSIGNMENT     = OpDef(kw.ASSIGN, right_ass=True)

