from tests.ldatestcase import LDATestCase
from lda.errors import semantic

class TestUnreachableStatement(LDATestCase):
	def test_unreachable_statement_in_algorithm(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				début
					retourne
					(**)retourne
				fin""")

	def test_unreachable_statement_in_while(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				début
					tantque vrai faire
						retourne
						(**)retourne
					ftant
				fin""")

	def test_unreachable_statement_after_while_always_returns(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				début
					tantque vrai faire
						retourne
					ftant
					(**)retourne
				fin""")

	def test_unreachable_statement_after_for_always_returns(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				lexique
					i: entier
				début
					pour i de 1 jusque 10 faire
						retourne
					fpour
					(**)retourne
				fin""")

	def test_still_reachable_statement_after_if_returns(self):
		self.check(program="""\
				algorithme
				début
					si 1+1=2 alors
						retourne
					fsi
					retourne
				fin""")

	def test_still_reachable_statement_after_both_if_and_elif_return(self):
		self.check(program="""\
				algorithme
				début
					si 1+1=2 alors
						retourne
					snsi 2+2=4 alors
						retourne
					fsi
					retourne
				fin""")

	def test_still_reachable_statement_after_one_if_clause_doesnt_return(self):
		self.check(program="""\
				algorithme
				début
					si 1+1=2 alors
						écrire("bidon")
					snsi 2+2=4 alors
						retourne
					sinon
						retourne
					fsi
					retourne
				fin""")

	def test_unreachable_statement_after_all_if_clauses_and_else_clause_return(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				début
					si 1+1=2 alors
						retourne
					snsi 2+2=4 alors
						retourne
					sinon
						retourne
					fsi
					(**)retourne
				fin""")

	def test_unreachable_statement_after_deeply_nested_return(self):
		self.assertLDAError(semantic.UnreachableStatement, analyzer=self.check,
				program="""\
				algorithme
				lexique
					i: entier
				début
					tantque vrai faire
						pour i de 1 jusque 3 faire
							si 1+1=2 alors
								retourne
							sinon
								retourne
							fsi
						fpour
					ftant
					(**)retourne
				fin""")

