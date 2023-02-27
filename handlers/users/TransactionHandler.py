from crud import CRUDUsers, CRUDTransaction, CRUDCurrency

from loader import bot


class TransactionHandler():

    @staticmethod
    async def Transaction_Confirmation(data: dict, message, check_number=False):

        try:
            get_user_id = int(data['id'])
            get_page_id = int(data['editId'])
            user = await CRUDUsers.get(id=get_user_id)

            if check_number:
                transaction = await CRUDTransaction.get(transaction=get_page_id)
                currency = await CRUDCurrency.get(currency_id=transaction.currency_id)

                transaction.approved = True
                await CRUDTransaction.update(transaction=transaction)
                text = f"✅ Вам потвердили сделку № {transaction.id} ✅\n\n" \
                       f"📈 Курс покупки: <i>{transaction.exchange_rate}\n</i>" \
                       f"   ₿  Куплено BTC: <i>{transaction.buy_BTC}\n</i>" \
                       f"💸 Продано {currency.name}: <i>{transaction.sale}\n</i>" \
                       f"👛 Кошелек <i>{transaction.wallet}</i>"

                await bot.send_message(chat_id=user.user_id, text=text)

                await message.answer(text="Вы успешно потвердили сделку")
            else:
                transaction = await CRUDTransaction.get_all(user_id=user.id)
                currency = await CRUDCurrency.get(currency_id=transaction[get_page_id].currency_id)

                transaction[get_page_id].approved = True
                await CRUDTransaction.update(transaction=transaction[get_page_id])
                text = f"✅ Вам потвердили сделку № {transaction[get_page_id].id} ✅\n\n" \
                       f"📈 Курс покупки: <i>{transaction[get_page_id].exchange_rate}\n</i>" \
                       f"   ₿  Куплено BTC: <i>{transaction[get_page_id].buy_BTC}\n</i>" \
                       f"💸 Продано {currency.name}: <i>{transaction[get_page_id].sale}\n</i>" \
                       f"👛 Кошелек <i>{transaction[get_page_id].wallet}</i>"

                await bot.send_message(chat_id=user.user_id, text=text)

                await message.answer(text="Вы успешно потвердили сделку")


        except Exception as e:
            print(e)
