import requests
from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic


class CreateWallet:

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
        data["wallet"] = {"passphrase": passphrase, "address": address}
        w.get_key()
        w.get_key(account_btc2.account_id)
        w.get_key(account_ltc1.account_id)
        w.info()
        return data

    @staticmethod
    async def get_balance(wallet: str):

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'
        }

        proxies = {
            'http': 'http://45.155.203.112:8000'
        }

        balance_url = f'https://blockchain.info/q/addressbalance/{wallet}'
        get_url = requests.get(url=balance_url, headers=headers, proxies=proxies)
        if get_url.status_code == 200:
            r = requests.get(balance_url)
            btc = int(r.text) / 100000000
            text1 = str(btc) + " BTC."
            return text1
        else:
            return False


