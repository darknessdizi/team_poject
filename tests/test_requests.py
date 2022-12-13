import unittest
import requests
import os

class Test_Requests(unittest.TestCase):
    def test_connection_to_vk(self):
        url = 'https://api.vk.com/method/users.search'
        access_token = os.getenv("access_token")
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {access_token}'}

        res = requests.get(url=url, headers=headers)
        self.assertEqual(res.status_code, 200)

