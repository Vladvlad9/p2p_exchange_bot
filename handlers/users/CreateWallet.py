from bit import PrivateKey
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
import requests
from fake_useragent import UserAgent


class CreateWallet:
    #wif_sender: str,
                             # btc_money: float,
                             # address_recipient: str
    @staticmethod
    async def money_transfer():
        my_key = PrivateKey(wif='')

        # Количество долларов перевода, можно поменять на btc
        money = 0.0000100
        # Кошелек куда будут переведены деньги
        wallet = '1Fu4oDBsNExmpidzXq9xUXkSZs9CLp8xdB'

        # Коммисия перевода, если поставить слишком маленькую, то транзакцию не примут
        # И чем больше коммисия, тем быстрее пройдет перевод
        fee = 2000

        # Генерация транзакции
        tx_hash = my_key.create_transaction([(wallet, money, 'btc')], fee=fee, absolute_fee=True)

        print(tx_hash)

    @staticmethod
    async def create_wallet(label: str) -> dict:
        data = {}
        passphrase = Mnemonic().generate()
        print(passphrase)
        w = Wallet.create(f"Wallet{str(label)}", keys=passphrase, network='bitcoin')
        account_btc2 = w.new_account('Account BTC 2')
        account_ltc1 = w.new_account('Account LTC', network='litecoin')
        key1 = w.get_key()
        address = key1.address
        private = key1.key_private
        wif = key1.wif
        data["wallet"] = {"passphrase": passphrase, "address": address, "wif": wif}

        w.get_key()
        w.get_key(account_btc2.account_id)
        w.get_key(account_ltc1.account_id)
        w.info()
        return data

    @staticmethod
    async def get_balance(wallet: str):
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        proxies = {
            'http': 'http://45.155.203.112:8000'
        }

        balance_url = f'https://blockchain.info/q/addressbalance/{wallet}'
        get_url = requests.get(url=balance_url, headers=headers)
        if get_url.status_code == 200:
            r = requests.get(balance_url)
            btc = int(r.text) / 100000000
            text1 = btc
            return text1
        else:
            return False


