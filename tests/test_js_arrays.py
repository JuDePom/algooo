from tests.ldatestcase import LDATestCase
from subprocess import CalledProcessError

class TestJSArrays(LDATestCase):

	def test_1d_static_integer_array_access_out_of_bounds(self):
		self.assertRaises(CalledProcessError, self.jseval, shutup=True, program="""\
				algorithme
				lexique
					t: tableau entier[1..10]
				début
					t[-999] <- 3
				fin""")

	def test_2d_dynamic_integer_array_access_out_of_bounds(self):
		self.assertRaises(CalledProcessError, self.jseval, shutup=True, program="""\
				algorithme
				lexique
					t: tableau entier[?]
				début
					tailletab(t, 100..110)
					t[-999] <- 30
				fin""")

