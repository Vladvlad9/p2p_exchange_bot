from decimal import Decimal

import aiohttp
import requests
from config import CONFIG
from fake_useragent import UserAgent
import urllib
from datetime import datetime
import xml.etree.ElementTree as ET


class Cryptocurrency:

    @staticmethod
    async def get_byn():
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
    async def get_rub1():
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
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
    async def get_rub():
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

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
                if price is None:
                    await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
                else:
                    return price
            else:
                print(get_request.status_code)
                return await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
        except Exception as e:
            await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")

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
        if get_usd is None:
            count = 0
            while get_usd is None:
                if count == 10:  # Что бы не войти в бесконечный цикл
                    break
                else:
                    count += 1
                    get_usd = await Cryptocurrency.get_Cryptocurrency("USD")

        if currency == 'BYN':
            get_byn = await Cryptocurrency.get_byn()
            byn: float = float(Decimal(get_byn) * Decimal(get_usd))
            return byn
        else:
            #get_rub = await Cryptocurrency.get_rub()
            #rub = float(Decimal(get_rub) * Decimal(get_usd))
            rub = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
            if rub is None:
                count_rub = 0
                while get_usd is None:
                    if count_rub == 10:  # Что бы не войти в бесконечный цикл
                        break
                    else:
                        count_rub += 1
                        rub = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
            return rub

    @staticmethod
    async def get_Cryptocurrency(currency: str) -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        url = ""
        if currency == 'USD':
            url = CONFIG.COINBASE.USD
        elif currency == 'BYN':
            url = CONFIG.COINBASE.BYN
        else:
            url = CONFIG.COINBASE.RUB

        post_price = 0
        #get_request = requests.get(url=url, headers=headers)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                try:
                    data = await response.json()
                    price = float(data["data"]["bitcoin"]["quote"]['price'])
                    round_price = round(price, 3)
                    post_price = float(round_price)
                    return post_price
                except Exception:
                    pass



        # try:
        #     if get_request.status_code == 200:
        #         data = get_request.json()
        #         price = float(data["data"]["bitcoin"]["quote"]['price'])
        #         round_price = round(price, 3)
        #         post_price = float(round_price)
        #         return post_price
        #
        #     else:
        #         print(get_request.status_code)
        # except Exception as e:
        #     if post_price != 0:
        #         return post_price
        #     await Cryptocurrency.get_Cryptocurrency("USD")

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


