from decimal import Decimal

import requests
from config import CONFIG
from fake_useragent import UserAgent
import urllib
from datetime import datetime
import xml.etree.ElementTree as ET


class Cryptocurrency:

    @staticmethod
    async def get_byn():
        get_request = requests.get(url="https://www.nbrb.by/api/exrates/rates/431")
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
    async def get_rub():
        try:
            current_datetime = datetime.now()
            month = current_datetime.month

            if month < 10:
                month = f"0{current_datetime.month}"

            url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={current_datetime.day}/" \
                  f"{month}/{current_datetime.year}"

            result = float(ET.fromstring(requests.get(url).text).find(
                './Valute[CharCode="USD"]/Value').text.replace(',', '.')
                           )
            return result
        except Exception as e:
            print(e)

    @staticmethod
    async def get_rub1():
        current_datetime = datetime.now()
        month = current_datetime.month

        if month < 10:
            month = f"0{current_datetime.month}"

        try:
            url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={current_datetime.day}/" \
                  f"{month}/{current_datetime.year}"
            get_request = requests.get(url=url)

            if get_request.status_code == 200:

                import xmltodict

                data = requests.get(url)
                xpars = xmltodict.parse(data.text)
                price = xpars['ValCurs']['Valute'][13]['Value'].replace(',', '.')
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_CryptocurrencyBTC(currency: str) -> float:
        if currency == 'RUB':
            url = CONFIG.COINBASE.BTC_RUB
        else:
            url = CONFIG.COINBASE.BTC_BYN

        get_request = requests.get(url=url)
        try:
            if get_request.status_code == 200:
                data = get_request.json()
                price = float(data["data"]["assetBySymbol"]["latestQuoteV3"]['price'])
                round_price = round(price, 3)
                return round_price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_update_currency(currency: str) -> float:
        get_usd = await Cryptocurrency.get_Cryptocurrency("USD")
        if currency == 'BYN':
            get_byn = await Cryptocurrency.get_byn()
            byn = float(Decimal(get_byn) * Decimal(get_usd))
            return byn
        else:
            get_rub = await Cryptocurrency.get_rub()
            rub = float(Decimal(get_rub) * Decimal(get_usd))
            return rub

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


