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
	def __init__(self, pos, body):
		SourceThing.__init__(self, pos)
		self.body = body
	def __repr__(self):
		return "algorithme :\n{}".format(self.body)

class Function(SourceThing):
	def __init__(self, pos, name, fp_list, body):
		SourceThing.__init__(self, pos)
		self.name = name
		self.fp_list = fp_list
		self.body = body
	def __repr__(self):
		return "fonction {} :\n{}".format(self.name, self.body)

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
		return "affectation ({} <- {})".format(self.lhs, self.rhs)

class FunctionCall(Instruction):
	def __init__(self, pos, function_name, effective_parameters):
		self.function_name = function_name
		self.effective_parameters = effective_parameters
	def __repr__(self):
		return "appel de fonction {} avec paramètres {}".format(
				self.function_name, 
				self.effective_parameters)

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

