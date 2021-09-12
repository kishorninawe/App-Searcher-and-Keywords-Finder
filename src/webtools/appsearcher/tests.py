from django.test import TestCase, Client


class TestPage(TestCase):
    def setUp(self):
        self.client = Client()

    def check_data_is_valid(self, response):
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in data.keys():
            self.assertTrue(data[key] is not None or data[key] != '')
        self.assertEqual(data['app_name'], 'Void Troopers : Sci-fi Tapper')
        self.assertEqual(data['developer_name'], 'Appxplore (iCandy)')

    def test_search_app(self):
        response = self.client.get('/searchapp/')
        self.assertEqual(response.status_code, 200)

        # Check for app in google play store
        response = self.client.post('/searchapp/', {
            'package_name': 'com.appxplore.voidtroopers',
            'store': 'google'
        })
        self.check_data_is_valid(response)

        # Check for app in apple app store
        response = self.client.post('/searchapp/', {
            'app_name': 'Void Troopers : Sci-fi Tapper',
            'app_id': '1367822033',
            'store': 'apple'
        })
        self.check_data_is_valid(response)
