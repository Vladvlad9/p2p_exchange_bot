import requests
import pandas
from requests import HTTPError

from config import CONFIG


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
        #transactions_url = 'https://blockchain.info/rawaddr/' + "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"
        try:
            url = f'https://blockchain.info/rawaddr/{btc_address}'
            x = requests.get(url)
            wallet = x.json()
            return True
        except Exception as e:
            print(e)
            return False


