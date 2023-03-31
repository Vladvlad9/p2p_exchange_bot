import requests
from fake_useragent import UserAgent


class Cryptocurrency:

    @staticmethod
    async def get_byn() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        get_request = requests.get(url="https://www.nbrb.by/api/exrates/rates/431", headers=headers)
        try:
            if get_request.status_code == 200:
                data = get_request.json()
                price = float(data["Cur_OfficialRate"])
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_rub() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=USDTRUB"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_btc() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=BTCUSDT"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
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


