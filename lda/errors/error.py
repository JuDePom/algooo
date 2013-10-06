class LDAError(Exception):
	def __init__(self, pos, message):
		self.pos = pos
		self.message = message
		super().__init__("{} : {}".format(pos.terse(), message))

	def pretty(self, buf):
		message = "{} : {}".format(self.pos.pretty(), self.message)
		if hasattr(self, 'intent'):
			message += "\n(Lors de l'analyse de : {})".format(self.intent)
		if hasattr(self, 'tip'):
			message += "\n(Conseil : {})".format(self.tip)
		line, tick = self.pos.marker_lines(buf)
		message += "\n\t{}\n\t{}".format(line, tick)
		return message

