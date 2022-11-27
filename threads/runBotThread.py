from threads.swapTokensThread import SwapTokens
from PyQt5.QtCore import QThread, pyqtSignal
from bots.cake_bot import Bot
from bots import utils

import pandas as pd
import time
import os

# Amount Change Thread Class
class RunBot(QThread):

    any_signal = pyqtSignal(str)

    def __init__(   self,
                    textBoxInputs,
                    token0,
                    token1,
                    bot,
                    bot_idx,
                    parent=None,
                    index=979) -> None:
        super(RunBot, self).__init__(parent)
        self.textBoxInputs = textBoxInputs
        self.is_running = True
        self.token0 = utils.search_token(token0, bot.tokens)
        self.token1 = utils.search_token(token1, bot.tokens)
        self.transaction_complete = False
        self.bot_idx = bot_idx
        self.index = index
        self.buy_bot = bot
        self.sell_bot = self.create_sell_bot()

    def create_sell_bot(self):
        bot = Bot(utils.load_setting('pancakeswap'))
        bot.set_address(self.buy_bot.address, self.buy_bot.private_key)
        bot.set_contract_get_price_func(self.token1['SYMBOL'], self.token0['SYMBOL'])
        return bot

    def stop(self):
        print('Stopping thread...', self.index)
        self.is_running = False
        self.terminate()

    def update_transaction(self, tx_hash, address, tx_status):
        self.tx_hash = tx_hash
        self.tx_status = tx_status
        self.transaction_complete = True

        # Record transaction in a csv file
        data = {
                'DATETIME': 1,
                'TX_HASH': tx_hash, 
                'TX_STATUS': tx_status,
                'ADDRESS': address,
                'TOKEN0': self.token0['SYMBOL'],
                'TOKEN1': self.token1['SYMBOL'],
                'AMOUNT': self.amount
                }

        csv_path = utils.get_path(['bot_transactions', f'bot_{self.bot_idx}.csv'])
        if os.path.isfile(csv_path):
            df = pd.read_csv(csv_path, index_col=None)
            df = df.append(data, ignore_index=True)
        else:
            df = pd.DataFrame(data, index=[0])
        
        df.to_csv(csv_path, index=None)

    def _initiate_swap_transaction(self, amount, type='buy'):
        token0 = self.token0 if type == 'buy' else self.token1
        token1 = self.token1 if type == 'buy' else self.token0

        print(f"Initiating a {type} transaction")

        price = self.sell_bot.get_price()
        amount = amount if type == 'buy' else amount * (float(price) if price != '-' else 0.0)

        # Start swapping thread
        swapThread = SwapTokens(token0, token1,
                                amount, 
                                self.buy_bot if type == 'buy' else self.sell_bot)
        swapThread.setTerminationEnabled(True)
        swapThread.start()
        swapThread.any_signal.connect(self.update_transaction)

        print(f"Waiting for {type} transaction to complete!")
        while not self.transaction_complete:
            pass

        print(f"{self.tx_hash} was a {self.tx_status.lower()}")
        swapThread.stop()

        self.bought =   1 \
                        if ('Success' in self.tx_status and type == 'buy') or ('Fail' in self.tx_status) \
                        else 0

        # Separating Profits
        # Storing the price at buy time
        if type == 'buy':
            self.buying_price = 1 / float(self.buy_bot.get_price())
        
        if type == 'sell':
            profit = (float(self.sell_bot.get_price()) * self.amount) - (self.buying_price * self.amount + 1)
            
            # Initiate transfer to a defined wallet
            print("transfer_tx:", self.buy_bot.transfer(self.token0, self.wallet_address, profit * (self.profit_to_transfer / 100)))

    def run(self):
        print('Starting thread...', self.index)

        stop_loss = float(self.textBoxInputs[1].text())
        buy_price = float(self.textBoxInputs[2].text())
        sell_price = float(self.textBoxInputs[3].text())
        self.wallet_address = self.textBoxInputs[4].text()
        self.profit_to_transfer = self.textBoxInputs[5].value()
        print(self.profit_to_transfer, type(self.profit_to_transfer))

        error = True
        self.amount = float(self.textBoxInputs[0].text())
        self.bought = 0
        
        # DEBUG
        print(buy_price, sell_price, stop_loss, 1 / float(self.buy_bot.get_price()), float(self.sell_bot.get_price()))

        while self.is_running:
            
            try:
                # Buying and selling tokens
                # WIP: integrate slippage 
                # Buy tokens at a certain price
                if 1 / float(self.buy_bot.get_price()) <= buy_price and not self.bought:
                    self._initiate_swap_transaction(self.amount)

                # Sell tokens at a certain price
                if float(self.sell_bot.get_price()) >= sell_price and self.bought:
                    self._initiate_swap_transaction(self.amount, type='sell')

                # Stop loss at a certain price
                if float(self.sell_bot.get_price()) <= stop_loss and self.bought:
                    self._initiate_swap_transaction(self.amount, type='sell')

                error = True
            except ValueError as v:
                if error:
                    print("Connection error!")

                error = False