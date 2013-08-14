def format_tree(module):
	result = ""
	if module.algorithm is not None:
		result += module.algorithm.lda_format(0)
	for func in module.functions:
		result += func.lda_format(0)
	return result