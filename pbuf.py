class ParserBuffer:
	text = None

	def load_file(self, path):
		with open(path, 'r') as input_file:
			self.text = input_file.read()
			print(self.text)
	

# rather than using a singleton we're going to imitate random.py
# http://hg.python.org/cpython/file/3.3/Lib/random.py#l702
# reminder: identifiers starting with _ will not be exported to other modules

_inst = ParserBuffer()
load_file = _inst.load_file

print("static ParserBuffer initialized")

