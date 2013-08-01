'''
Items that make up the abstract syntax tree.
'''

class SourceThing:
	'''
	Anything that can represented in a source file.
	'''
	def __init__(self, pos):
		self.pos = pos

class Keyword(SourceThing):
	def __init__(self, pos, kwdef):
		SourceThing.__init__(self, pos)
		self.kwdef = kwdef

class Identifier(SourceThing):
	def __init__(self, pos, name_string):
		SourceThing.__init__(self, pos)
		self.name_string = name_string
	def __str__(self):
		return "id \'{}\'".format(self.name_string)

class FormalParameter(SourceThing):
	def __init__(self, pos, name_identifier, type_kw):
		SourceThing.__init__(self, pos)
		self.name_id = name
		self.type_kw = type_kw

#######################################################################
#
# TOP-LEVEL
#
#######################################################################

class Algorithm(SourceThing):
	def __init__(self, pos, lexicon, body):
		SourceThing.__init__(self, pos)
		self.body = body
		self.lexicon = lexicon
	def __repr__(self):
		return "algorithme :\n{}\n{}".format(self.lexicon, self.body)

class Function(SourceThing):
	def __init__(self, pos, name, fp_list, lexicon, body):
		SourceThing.__init__(self, pos)
		self.name = name
		self.fp_list = fp_list
		self.lexicon = lexicon
		self.body = body
	def __repr__(self):
		return "fonction {} :\n{}\n{}".format(self.name, self.lexicon, self.body)

#######################################################################
#
# LEXICON
#
#######################################################################

class Lexicon(SourceThing):
	def __init__(self, pos, body):
		SourceThing.__init__(self, pos)
		self.body = body
	def __repr__(self):
		return "lexique : \n{}".format(self.body)
	
class Declaration(SourceThing):
	def __init__(self, pos, identifier, type_kw):
		SourceThing.__init__(self, pos)
		self.identifier = identifier
		self.type_kw = type_kw
	def __repr__(self):
		return "déclaration ({} : {})\n".format(self.identifier, self.type_kw)
		
#######################################################################
#
# INSTRUCTIONS
#
#######################################################################

class Instruction(SourceThing):
	def __init__(self, pos):
		SourceThing.__init__(self, pos)

class Assignment(Instruction):
	def __init__(self, pos, lhs, rhs):
		Instruction.__init__(self, pos)
		self.lhs = lhs
		self.rhs = rhs
	def __repr__(self):
		return "affectation ({} <- {})\n".format(self.lhs, self.rhs)
	
class FunctionCall(Instruction):
	def __init__(self, pos, function_name, effective_parameters):
		self.function_name = function_name
		self.effective_parameters = effective_parameters
	def __repr__(self):
		return "appel de fonction {} avec paramètres {}\n".format(
				self.function_name, 
				self.effective_parameters)

class InstructionIf(Instruction):
	def __init__(self, pos, bool_Expr, first_block, optional_block=None ):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.first_block = first_block
		self.optional_block = optional_block
	def __repr__(self):
		if self.optional_block is None:
			return "si {} alors \n{}fsi\n".format(self.bool_Expr, self.first_block)
		else :
			return "si {} alors \n{}sinon \n{}fsi\n".format(self.bool_Expr, self.first_block, self.optional_block)

class InstructionFor(Instruction):
	def __init__(self, pos, increment, int_from, int_to, block):
		Instruction.__init__(self, pos)
		self.increment = increment
		self.int_from = int_from
		self.int_to = int_to
		self.block = block		
	def __repr__(self):
		return "pour {} de {} a {} faire \n{}fpour\n".format(self.increment, self.int_from, self.int_to, self.block)

class InstructionForEach(Instruction):
	def __init__(self, pos, element, list_element, block):
		Instruction.__init__(self, pos)
		self.element = element
		self.list_element = list_element
		self.block = block	
	def __repr__(self):
		return "pour chaque {} dans {} faire \n{}fpour\n".format(self.element, self.list_element, self.block)

class InstructionWhile(Instruction):
	def __init__(self, pos, bool_Expr, block):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.block = block	
	def __repr__(self):
		return "tantque {} faire \n{}ftant\n".format(self.bool_Expr, self.block)

class InstructionDoWhile(Instruction):
	def __init__(self, pos, block, bool_Expr):
		Instruction.__init__(self, pos)
		self.block = block
		self.bool_Expr = bool_Expr	
	def __repr__(self):
		return "répéter \n{} \njusqu'à {}\n".format(self.block, self.bool_Expr)
		
		
#######################################################################
#
# EXPRESSIONS
#
#######################################################################

class Expression(SourceThing):
	def __init__(self, pos):
		SourceThing.__init__(self, pos)

class LiteralInteger(Expression):
	def __init__(self, pos, value):
		Expression.__init__(self, pos)
		self.value = value
	def __repr__(self):
		return "entier littéral " + str(self.value) 

class LiteralReal(Expression):
	def __init__(self, pos, value):
		Expression.__init__(self, pos)
		self.value = value
	def __repr__(self):
		return "réel littéral " + str(self.value)

class LiteralString(Expression):
	def __init__(self, pos, value):
		Expression.__init__(self, pos)
		self.value = value
	def __repr__(self):
		return "chaîne littérale \"" + self.value + "\""

class LiteralBoolean(Expression):
	def __init__(self, pos, value):
		Expression.__init__(self, pos)
		self.value = value
	def __repr__(self):
		return "booléen littéral " + str(self.value)

