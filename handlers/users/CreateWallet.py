import ecdsa
import hashlib
import base58
import requests

from bit import PrivateKey
from fake_useragent import UserAgent


class CreateWallet:
    @staticmethod
    async def money_transfer(wif_sender: str, btc_money: float, address_recipient: str):
        my_key = PrivateKey(wif=wif_sender)

        # Количество долларов перевода, можно поменять на btc
        #money = 0.0000100
        # Кошелек куда будут переведены деньги
        #wallet = '1Fu4oDBsNExmpidzXq9xUXkSZs9CLp8xdB'

        # Коммисия перевода, если поставить слишком маленькую, то транзакцию не примут
        # И чем больше коммисия, тем быстрее пройдет перевод
        fee = 200

        # Генерация транзакции
        tx_hash = my_key.create_transaction([(address_recipient, btc_money, 'btc')], fee=fee, absolute_fee=True)

        print(tx_hash)
        return tx_hash

    @staticmethod
    async def money_text():
        my_key = PrivateKey(wif="5JZxopabxNnKMurLwSZGDsUc5RxA7pkkugHjfkqgohTmkt6Nqg7")
        #1Fu4oDBsNExmpidzXq9xUXkSZs9CLp8xdB - 5JZxopabxNnKMurLwSZGDsUc5RxA7pkkugHjfkqgohTmkt6Nqg7
        # Количество долларов перевода, можно поменять на btc
        money = 0.00004
        # Кошелек куда будут переведены деньги
        wallet = '13DN5vbhW1UNE5gZLVoALH233qPMvvEZs4'

        # Коммисия перевода, если поставить слишком маленькую, то транзакцию не примут
        # И чем больше коммисия, тем быстрее пройдет перевод
        fee = 200

        # Генерация транзакции
        tx_hash = my_key.create_transaction([(wallet, money, 'btc')], fee=fee, absolute_fee=True)

        print(tx_hash)
        return tx_hash

    @staticmethod
    async def new_create_wallet(private_key):
        # Convert WIF private key to binary format
        private_key_bytes = base58.b58decode_check(private_key)[1:]

        # Generate public key from private key
        secp256k1_curve = ecdsa.curves.SECP256k1
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=secp256k1_curve)
        verifying_key = signing_key.get_verifying_key()
        public_key_bytes = bytes.fromhex("04") + verifying_key.to_string()

        # Hash the public key with SHA-256 and RIPEMD-160
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripe160_hash = hashlib.new("ripemd160", sha256_hash).digest()

        # Add network byte (0x00 for mainnet) and checksum
        version_ripe160_hash = bytes.fromhex("00") + ripe160_hash
        checksum = hashlib.sha256(hashlib.sha256(version_ripe160_hash).digest()).digest()[:4]
        address_bytes = version_ripe160_hash + checksum

        # Encode the address in base58
        address = base58.b58encode(address_bytes).decode()

        return address

    @staticmethod
    async def create_wallet() -> dict:
        data = {}
        # passphrase = Mnemonic().generate()
        # print(passphrase)
        # w = Wallet.create(f"Wallet{str(label)}", keys=passphrase, network='bitcoin')
        # account_btc2 = w.new_account('Account BTC 2')
        # account_ltc1 = w.new_account('Account LTC', network='litecoin')
        # key1 = w.get_key()
        # address = key1.address
        # private = key1.key_private
        # wif = key1.wif
        # data["wallet"] = {"passphrase": passphrase, "address": address, "wif": wif}
        #
        # w.get_key()
        # w.get_key(account_btc2.account_id)
        # w.get_key(account_ltc1.account_id)
        # w.info()

        # Generate a new private key
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

        # Convert the private key to WIF format
        extended_key_bytes = b'\x80' + private_key.to_string()
        checksum = hashlib.sha256(hashlib.sha256(extended_key_bytes).digest()).digest()[:4]
        wif_bytes = extended_key_bytes + checksum
        wif = base58.b58encode(wif_bytes).decode()

        # Generate the public key from the private key
        public_key = private_key.get_verifying_key().to_string()

        # Generate the Bitcoin address from the public key
        public_key_hash = hashlib.sha256(public_key).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(public_key_hash)
        ripemd160_hash = ripemd160.digest()
        address_bytes = b'\x00' + ripemd160_hash
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        #address = base58.b58encode(address_bytes + checksum).decode()

        address = await CreateWallet.new_create_wallet(wif)

        data['wallet'] = {"address": address, "wif": wif}
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


