from django.test import TestCase, Client


# Create your tests here.
class TestPage(TestCase):
	def setUp(self):
		self.client = Client()

	def test_index(self):
		response = self.client.get('/appsearch/')
		self.assertEqual(response.status_code, 200)

	def check_data_is_valid(self, response):
		self.assertEqual(response.status_code, 200)
		data = response.json()
		try:
			self.assertTrue(data['error_message'] != None
							or data['error_message'] != '')
		except KeyError:
			for key in data.keys():
				self.assertTrue(data[key] != None or data[key] != '')
			self.assertEqual(data['app_name'], 'Void Troopers : Sci-fi Tapper')
			self.assertEqual(data['developer_name'], 'Appxplore (iCandy)')

	def test_app_search(self):
		# Check for app in google play store
		response = self.client.get('/search_app/', {
			'package_name': 'com.appxplore.voidtroopers',
			'store': 'google'
		})
		self.check_data_is_valid(response)
		# Check for app in apple app store
		response = self.client.get(
			'/search_app/', {
				'app_name': ' Void Troopers : Sci-fi Tapper',
				'app_id': '1367822033',
				'store': 'apple'
			})
		self.check_data_is_valid(response)
