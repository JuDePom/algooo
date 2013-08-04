_node_id_counter = 0

_node_cache = {}
def _fresh_id():
	global _node_id_counter
	i = _node_id_counter
	_node_id_counter += 1
	return i

class Node:
	def __init__(self, label, cluster, *children):
		self.oid = str(_fresh_id())
		self.label = label
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
		self.label = label
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

def graph_program(top_level):
	supercluster = Cluster("programme")
	for t in top_level:
		t.put_node(supercluster)
	all_nodes = supercluster.node_cascade()

	s = "digraph program {\nnode [shape=plaintext, height=0];\n\n"
	s += ''.join([sc.dump_contents() for sc in supercluster.subclusters])
	s += ''.join([n.dump_def() for n in all_nodes])
	s += ''.join([n.dump_links() for n in all_nodes])
	s += "}\n"

	return s

