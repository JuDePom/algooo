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
	def __init__(self, symbol, name="???", precedence=None, unary=False, right_ass=False,
	             encompass_till=None, encompass_several=False):
		if precedence is None:
			# we can't put _current_pg as the default value for precedence
			# because it's not resolved at runtime...
			precedence = _current_pg
		self.precedence     = precedence
		self.symbol         = symbol
		self.name           = name
		self.unary          = unary 
		self.right_ass      = right_ass
		self.encompass_till = encompass_till
		self.encompass_several = encompass_several
		self.binary         = not unary
		self.left_ass       = not right_ass
		if self.binary:
			meta.all_binaries.append(self)
		else:
			meta.all_unaries.append(self)

	def __repr__(self):
		return str(self.symbol)


_new_precedence_group()
SUBSCRIPT      = OpDef(kw.LSBRACK, "souscription de tableau",
                       encompass_till=kw.RSBRACK, encompass_several=True)
FUNCTION_CALL  = OpDef(kw.LPAREN, "appel de fonction",
                       encompass_till=kw.RPAREN, encompass_several=True)
MEMBER_SELECT  = OpDef(kw.DOT, "sélection de membre")
UNARY_MINUS    = OpDef(kw.MINUS, "- unaire", unary=True, right_ass=True)
UNARY_PLUS     = OpDef(kw.PLUS, "+ unaire", unary=True, right_ass=True)
NOT            = OpDef(kw.NOT, "NON logique", unary=True, right_ass=True)

_new_precedence_group()
POWER          = OpDef(kw.POWER, "puissance", right_ass=True)

_new_precedence_group()
MULTIPLICATION = OpDef(kw.TIMES, "multiplication")
DIVISION       = OpDef(kw.SLASH, "division")
MODULO         = OpDef(kw.MODULO, "modulo")

_new_precedence_group()
SUBTRACTION    = OpDef(kw.MINUS, "soustraction")
ADDITION       = OpDef(kw.PLUS, "addition")

_new_precedence_group()
RANGE          = OpDef(kw.DOTDOT, "intervalle")

_new_precedence_group()
LT             = OpDef(kw.LT, "inférieur")
GT             = OpDef(kw.GT, "supérieur")
LE             = OpDef(kw.LE, "inférieur ou égal")
GE             = OpDef(kw.GE, "supérieur ou égal")

_new_precedence_group()
EQ             = OpDef(kw.EQ, "égal")
NE             = OpDef(kw.NE, "différent")

_new_precedence_group()
AND            = OpDef(kw.AND, "ET logique")

_new_precedence_group()
OR             = OpDef(kw.OR, "OU logique")

_new_precedence_group()
ASSIGNMENT     = OpDef(kw.ASSIGN, "affectation", right_ass=True)

