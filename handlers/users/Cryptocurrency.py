import requests

from config import CONFIG


class Cryptocurrency:

    @staticmethod
    async def get_Cryptocurrency() -> float:
        get_request = requests.get(url=CONFIG.COINBASE)
        if get_request.status_code == 200:
            data = get_request.json()
            price_BYN = float(data["data"]["bitcoin"]["quote"]['price'])
            round_price = round(price_BYN, 3)
            return round_price
        else:
            pass
