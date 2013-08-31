_node_id_counter = 0

def _fresh_id():
	global _node_id_counter
	i = _node_id_counter
	_node_id_counter += 1
	return i

def _sanitize_label(label):
	return label.replace('"', '\\"')

class Node:
	def __init__(self, label, cluster, *children):
		self.oid = str(_fresh_id())
		self.label = _sanitize_label(label)
		self.cluster = cluster
		self.children = list(children)
		self.cluster.nodes.append(self)
		self.shape = None
	def dump_def(self):
		extra = ""
		if self.shape is not None:
			extra += ", shape=" + self.shape
		return "{} [label=\"{}\"{}];\n".format(self.oid, self.label, extra)
	def dump_links(self):
		s = ""
		for c in self.children:
			s += "{} -> {};\n".format(self.oid, c.oid)
		return s

class Cluster:
	def __init__(self, label, parent_cluster=None):
		self.oid = "cluster" + str(_fresh_id())
		self.label = _sanitize_label(label)
		self.nodes = []
		self.subclusters = []
		self.rank_chains = []
		if parent_cluster is not None:
			parent_cluster.subclusters.append(self)
	def dump_contents(self, i=''):
		nodes = ""
		for n in self.nodes:
			nodes += n.oid + ";"
		contents = ""
		for c in self.subclusters:
			contents += c.dump_contents(2*i+'\t')
		for chain in self.rank_chains:
			contents += "{rank=same;"
			for n in chain:
				contents += n.oid + ";"
			contents += "}\n"
		return ('subgraph {1} {{\n'
				'label="{2}";\n'
				'{3}\n'
				'{4}}}\n').format(i, self.oid, self.label, nodes, contents)
	def node_cascade(self):
		cascade = list(self.nodes)
		for sc in self.subclusters:
			cascade.extend(sc.node_cascade())
		return cascade

def put_arglist_node(arglist, cluster):
	def make_arg_node(i, item):
		arg_node = Node("arg"+str(i), cluster)
		rhs_node = item.put_node(rhs_cluster)
		arg_node.children.append(rhs_node)
		return arg_node
	if not arglist:
		return Node("\u2205", cluster)
	rhs_cluster = Cluster("", cluster)
	arg_nodes = [ make_arg_node(i, item) for i, item in enumerate(arglist) ]
	for previous, current in zip(arg_nodes, arg_nodes[1:]):
		previous.children.append(current)
	cluster.rank_chains.append(arg_nodes)
	return arg_nodes[0]

def format(module):
	master = Cluster("")
	module.put_node(master)
	all_nodes = master.node_cascade()
	return (
			"digraph program {{\n"
			"charset=utf8;\n"
			"node [shape=plaintext, height=0];\n"
			"\n"
			"{subclusters}\n"
			"{defs}\n"
			"{links}\n"
			"}}\n").format(
			subclusters = ''.join(sc.dump_contents() for sc in master.subclusters),
			defs = ''.join(n.dump_def() for n in all_nodes),
			links = ''.join(n.dump_links() for n in all_nodes))

