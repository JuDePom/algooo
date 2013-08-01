import ldakeywords as kw

_highest_pg = 5
_current_pg = _highest_pg
def _new_precedence_group():
	global _current_pg
	_current_pg -= 1

class Op:
	def __init__(self, symbol, precedence=_current_pg, unary=False, right_ass=False, encompass_till=None):
		self.precedence     = precedence
		self.symbol         = symbol
		self.unary          = unary 
		self.right_ass      = right_ass
		self.encompass_till = encompass_till
		self.binary         = not unary
		self.left_ass       = not right_ass

	def __repr__(self):
		return self.symbol + str(self.precedence)


_new_precedence_group()
SUBSCRIPT      = Op(kw.LSBRACK, encompass_till=kw.RSBRACK),
UNARY_MINUS    = Op(kw.MINUS, unary=True, right_ass=True),
UNARY_PLUS     = Op(kw.PLUS, unary=True, right_ass=True),
NOT            = Op(kw.NOT, unary=True, right_ass=True),

_new_precedence_group()
POWER          = Op(kw.POWER, right_ass=True),

_new_precedence_group()
MULTIPLICATION = Op(kw.TIMES)
DIVISION       = Op(kw.SLASH)
MODULO         = Op(kw.MODULO)

_new_precedence_group()
LT             = Op(kw.LT)
GT             = Op(kw.GT)
LE             = Op(kw.LE)
GE             = Op(kw.GE)

_new_precedence_group()
EQ             = Op(kw.EQ)
NE             = Op(kw.NE)

_new_precedence_group()
AND            = Op(kw.AND)

_new_precedence_group()
OR             = Op(kw.OR)

