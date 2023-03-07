import requests

from config import CONFIG
from fake_useragent import UserAgent
import urllib


class Cryptocurrency:

    @staticmethod
    async def get_Cryptocurrency(currency: str) -> float:
        url = ""
        if currency == 'USD':
            url = CONFIG.COINBASE.USD
        elif currency == 'BYN':
            url = CONFIG.COINBASE.BYN
        else:
            url = CONFIG.COINBASE.RUB

        get_request = requests.get(url=url)
        try:
            if get_request.status_code == 200:
                data = get_request.json()
                price = float(data["data"]["bitcoin"]["quote"]['price'])
                round_price = round(price, 3)
                return round_price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def Check_Wallet(btc_address: str) -> bool:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        # http://45.155.203.112:8000
        proxies = {
            'http': 'http://45.155.203.112:8000'
        }

        try:
            url = f'https://blockchain.info/q/addressbalance/{btc_address}'

            get_url = requests.get(url=url, headers=headers)
            if get_url.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False


