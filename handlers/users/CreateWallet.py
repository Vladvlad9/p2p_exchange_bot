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

