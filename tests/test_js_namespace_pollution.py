from tests import ldatestcase

class TestJSNamespacePollution(ldatestcase.LDATestCase):
	def test_js_global_namespace_pollution(self):
		# these must not pollute the global namespace
		extra1 = ''.join(
				"if (typeof {0} !== 'undefined') throw new Error('{0} should NOT be defined')\n".format(x)
				for x in ("$a", "$b", "$c", "$x", "$y", "$z", "$M", "$f",
					"P.$a", "P.$b", "P.$c", "P.$x", "P.$y"))
		# these MUST be in P
		extra2 = ''.join(
				"if (typeof {0} === 'undefined') throw new Error('{0} SHOULD be defined')\n".format(x)
				for x in ("P.$f", "P.main", "P.$M", "P.$z"))
		self.jseval(extracode="P.main();\n"+extra1+extra2, program="""\
				lexique
					M = <x: entier, y: entier>
					z: entier

				fonction f(a: entier)
				lexique
					b: entier
				début
				fin

				algorithme
				lexique
					c: entier
				début
					c <- 123
					f(c)
				fin""")


