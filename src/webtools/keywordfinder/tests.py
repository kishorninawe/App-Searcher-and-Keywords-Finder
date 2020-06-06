from django.test import TestCase, Client


# Create your tests here.
class TestPage(TestCase):
	def setUp(self):
		self.client = Client()

	def test_index(self):
		response = self.client.get('/keywordfind/')
		self.assertEqual(response.status_code, 200)
