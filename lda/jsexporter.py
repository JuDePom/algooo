class JSExporter:
	"""
	Facilitates the making of a properly-indented JS source file.
	"""

	def __init__(self):
		self.indent = 0
		self.strings = []
		self.already_indented = False

	def put(self, *items):
		"""
		Append items to the JS source code at the current indentation level.
		If an item is a string, append it right away; otherwise, invoke
		`item.JS(self)`.
		"""
		for i in items:
			if type(i) is str:
				if not self.already_indented:
					self.strings.append('\t' * self.indent)
					self.already_indented = True
				self.strings.append(i)
			else:
				i.js(self)

	def indented(self, exportfunc, *args):
		"""
		Append items to the source code at an increased indentation level.
		:param exportfunc: export function. Typically put, putline, or join.
		:param args: arguments passed to exportfunc
		"""
		self.indent += 1
		exportfunc(*args)
		self.indent -= 1

	def newline(self, count=1):
		"""
		Append line breaks to the source code.
		:param count: optional number of line breaks (default: 1)
		"""
		self.strings.append(count*'\n')
		self.already_indented = False

	def putline(self, *items):
		"""
		Append items to the source code, followed by a line break.
		"""
		self.put(*items)
		self.newline()

	def join(self, iterable, gluefunc, *args):
		"""
		Concatenate the elements in the iterable and append them to the source code.
		A 'glue' function (typically put()) is called between each element.
		Note : This method is similar in purpose to str.join().
		:param gluefunc: glue function called between each element
		:param args: arguments passed to gluefunc
		"""
		if not iterable:
			return
		it = iter(iterable)
		self.put(next(it))
		for element in it:
			gluefunc(*args)
			self.put(element)

	def __repr__(self):
		"""
		Return the source code built so far.
		"""
		return ''.join(self.strings)

