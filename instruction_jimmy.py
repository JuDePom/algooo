class InstructionBlock(Instruction):
	def __init__(self, pos, body):
		Instruction.__init__(self, pos)
		self.body = body

	def __repr__(self):
		return "\{ {} \{".format(self.body)



class InstructionIf(Instruction):
	def __init__(self, pos, bool_Expr, first_block, optional_block ):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.first_block = first_block
		self.optional_block = optional_block

	def __repr__(self):
		if self.f_block is None:
			return "si {} alors \n {} \n fsi".format(self.bool_Expr, self.first_block)
		else :
			return "si {} alors \n {} \n sinon {} fsi".format(self.bool_Expr, self.first_block, self.optional_block)



class InstructionFor(Instruction):
	def __init__(self, pos, increment, int_from, int_to, block):
		Instruction.__init__(self, pos)
		self.increment = increment
		self.int_from = int_from
		self.int_to = int_to
		self.block = block
		
	def __repr__(self):
		return "pour {} de {} a {} faire \n {} \n fpour".format(self.increment, self.int_from, self.int_to, self.block)



class InstructionForEach(Instruction):
	def __init__(self, pos, element, list_element, block):
		Instruction.__init__(self, pos)
		self.element = element
		self.list_element = list_element
		self.block = block
	
	def __repr__(self):
		return "pour chaque {} dans {} faire \n {} \n fpour".format(self.element, self.list_element, self.block)



class InstructionWhile(Instruction):
	def __init__(self, pos, bool_Expr, block):
		Instruction.__init__(self, pos)
		self.bool_Expr = bool_Expr
		self.block = block
		
	def __repr__(self):
		return "tantque {} faire \n {} \n  ftant".format(self.bool_Expr, self.block)



class InstructionDoWhile(Instruction):
	def __init__(self, pos, block, bool_Expr):
		Instruction.__init__(self, pos)
		self.block = block
		self.bool_Expr = bool_Expr
		
	def __repr__(self):
		return "repeter \n {} \n jusqu\'a {}".format(self.block, self.bool_Expr)