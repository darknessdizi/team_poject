import unittest
import requests
import token_vk
import requests_to_vk

access_token = token_vk.token_vk
version = '5.131'
params = {'access_token': access_token, 'v': version}
headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {access_token}'}


class Test_Requests(unittest.TestCase):
    def setUp(self):
        print('method setup')

    def tearDown(self) -> None:
        print('method tearDown')

    def test_connection_to_vk(self):
        url = 'https://api.vk.com/method/users.search'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {access_token}'}
        res = requests.get(url=url, headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_get_users_photo(self):

        vk = requests_to_vk.RequestsVk(access_token)
        res = vk.get_users_photo('710698165')
        self.assertEqual(res,  {'href': [
            'https://sun9-58.userapi.com/impg/ppqfXOzMK57-a9iMolIS9Dhqfi-sRmLpT_wI9g/kDoQfA24XGs.jpg?size=510x382'
            '&quality=95&sign=0d5b417d5b22a6e024f8fd21917d5d31&c_uniq_tag=NrnjU06c0ZkledojhaaQMr2oKOiW4smHPlF5qHYUURM'
            '&type=album',
            'https://sun6-22.userapi.com/impg/uju6BTi1PCIkJgrVvLQUlJYOvqZw3QaseVvH_Q/tDeOEiPOnIs.jpg?size=510x382'
            '&quality=95&sign=50d46f35a9404fa622677e17bfc0536a&c_uniq_tag=6vxiOglWdUoQVARyvU-weaLvjUnELOliXKx7fPBXqHU'
            '&type=album',
            'https://sun9-12.userapi.com/impg/FDR76Xlb_LWgrA0F-WXpIg8RWD11N-pK9yJcDA/B1f64xp-c-g.jpg?size=510x680'
            '&quality=95&sign=df5ac24c4523b6c9ca3d304fef37b4f3&c_uniq_tag=Wi5C6S2DohsJPnbjtUT7SEvNL92K0xpr7uPWvsDKl8M'
            '&type=album'],
                               'owner_id': '710698165'})


if __name__ == "__main__":
    unittest.main()


