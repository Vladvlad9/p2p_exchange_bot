import requests
import pandas
from requests import HTTPError

from config import CONFIG
from bit import PrivateKeyTestnet


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
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'
        }

        proxies = {
            'http': 'http://45.155.203.112:8000'
        }

        try:
            url = f'https://blockchain.info/q/addressbalance/{btc_address}'
            #get_url = requests.get(url)
            get_url = requests.get(url=url, headers=headers, proxies=proxies)
            if get_url.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False


