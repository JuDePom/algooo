"""
Parser facilities.
"""


from . import position
from .errors import syntax


def opening_keyword(keyword):
	"""
	Decorator for 'analyze_' methods.

	Try parsing an opening keyword before running the decorated method; if the
	opening keyword cannot be found, return None and do not run the decorated
	method.

	The decorated method is required to have `kwpos` as its first argument
	(position of the successfully-parsed opening keyword).

	If the optional argument `critical` is truthy when calling a decorated
	method, an ExpectedKeyword exception will be raised instead of returning
	None if the opening keyword is missing.
	"""
	def decorator(parser_method):
		def wrapper(self, *args, **kwargs):
			kwargs['kwpos'] = self.pos
			if 'critical' in kwargs:
				critical = kwargs['critical']
				del kwargs['critical']
			else:
				critical = False
			if critical:
				self.hardskip(keyword)
			elif not self.softskip(keyword):
				return None
			return parser_method(self, *args, **kwargs)
		return wrapper
	return decorator


class BaseParser:
	"""
	Builds up an AST from source code.
	
	This is a base class that does not contain parsing logic for any specific
	language; it is intended to provide convenient parsing tools to its
	subclasses.

	The "analyze_" functions check for the presence of a specific item at the
	current position in the buffer. There are three outcomes for a call to
	most analysis functions:

	- Found: the item was found. The current position in the buffer is moved
	  past the end of the item (skipping any whitespace that follows it), and
	  the item is returned.

	- Not found: the item was not found. Returns None. The current position in
	  the buffer is left as it was before calling the function.

	- Error: the item was partially found. However, a syntax error prevented
	  the parser from fully constructing the item. A SyntaxError exception is
	  raised and the current position is left where the parser managed to make
	  inroads.
	"""

	def __init__(self, options, buf, path):
		assert hasattr(self, 're_identifier'), "please provide re_identifier"
		self.raw_buf = buf
		self.path = path or "<string>"
		# set position to start of buffer
		self.pos = position.Position(self.path)
		self.buflen = len(self.raw_buf)
		# last regex match, used to report slightly more useful errors
		self.last_match = None
		self.last_match_pos = None
		# raw_buf is only used to parse strings and characters, and buf is used
		# for everything else. This separation allows for case insensitivity
		# while retaining the case in literal strings/characters.
		if options.ignore_case:
			self.buf = self.raw_buf.lower()
		else:
			self.buf = self.raw_buf
		# skip initial whitespace
		self.advance()

	@property
	def last_good_match(self):
		"""
		Return the last successful regular expression match. Can be used to
		report slightly friendlier syntax errors.
		"""
		if self.last_match is not None and self.last_match_pos == self.pos:
			return self.last_match

	def advance(self, chars=0):
		"""
		Advance current position in the buffer so that the cursor points on something
		significant (i.e. no whitespace, no comments)

		This function must be called at the very beginning of a source file, and
		after every operation that permanently consumes bytes from the buffer.
		"""
		bpos = self.pos.char
		line = self.pos.line
		column = self.pos.column
		if chars != 0:
			bpos += chars
			column += chars
		multi_start = None
		while bpos < self.buflen:
			if self.buf[bpos] == '\n':
				bpos += 1
				line += 1
				column = 1
			elif not multi_start:
				if self.buf[bpos].isspace():
					bpos += 1
					column += 1
				elif self.buf.startswith('(*', bpos):
					multi_start = position.Position(self.pos.path, bpos, line, column)
					bpos += 2
					column += 2
				elif self.buf.startswith('//', bpos):
					bpos = self.buf.find('\n', bpos+2)
					if bpos == -1:
						bpos = self.buflen
				else:
					break
			else:
				if self.buf.startswith('*)', bpos):
					multi_start = None
					bpos += 2
					column += 2
				else:
					bpos += 1
					column += 1
		if bpos == self.buflen and multi_start:
			raise syntax.UnclosedItem(multi_start, "commentaire multi-ligne non-fermé")
		self.pos = position.Position(self.pos.path, bpos, line, column)

	def eof(self):
		return self.pos.char >= self.buflen

	def _traverse_synonym_priority_chain(self, syn):
		"""
		Meant for BaseParser's internal use only!

		Return keyword synonym with highest priority over syn at the current
		position in the buffer, or return syn if syn must not give way to any
		synonym at the current position.
		"""
		for gw in syn.give_way:
			found = self._traverse_synonym_priority_chain(gw)
			if found is not None:
				return found
		if self.buf.startswith(syn.word, self.pos.char):
			return syn

	def _softskip1(self, keyword):
		"""
		Meant for BaseParser's internal use only!

		Consume a single keyword and return True, or return False if it cannot
		be found.
		"""
		cached_alpha = None
		for syn in keyword.synonyms:
			if syn.gluable:
				found = self._traverse_synonym_priority_chain(syn)
				if found is None:
					continue
				elif found == syn:
					# found this synonym
					self.advance(len(syn.word))
					return True
				else:
					# gave way to another keyword
					return
			else:
				if cached_alpha is None:
					cached_alpha = self.analyze_regex(self.re_identifier, advance=False)
					if cached_alpha is None:
						continue
				if cached_alpha == syn.word:
					self.advance(len(syn.word))
					return True

	def softskip(self, *choices):
		"""
		Consume and return a keyword among a set of choices, or return None if
		it cannot be found.
		"""
		for keyword in choices:
			if self._softskip1(keyword):
				return keyword

	def hardskip(self, *choices):
		"""
		Consume and return a keyword among a set of choices, or raise an
		ExpectedKeyword exception if it cannot be found.
		"""
		keyword = self.softskip(*choices)
		if keyword:
			return keyword
		raise syntax.ExpectedKeyword(self.pos, *choices,
				found_instead=self.last_good_match)

	def analyze_either(self, *analysis_order):
		"""
		Run the given analysis functions until an item can be returned, or
		return None if all the analysis functions failed.
		"""
		for analyze in analysis_order:
			o = analyze()
			if o is not None:
				return o

	def analyze_regex(self, compiled_regex, advance=True, buf=None):
		match = compiled_regex.match(buf or self.buf, self.pos.char)
		if match is None:
			return
		string = match.group(0)
		self.last_match, self.last_match_pos = string, self.pos
		if advance:
			self.advance(len(string))
		return string

